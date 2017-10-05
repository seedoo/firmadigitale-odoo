# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Innoviu srl (<http://www.innoviu.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import exceptions
from openerp import SUPERUSER_ID
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp import netsvc

import tempfile
import zipfile
import os
from datetime import datetime
import shutil
import subprocess
import hashlib
import random
import logging

_logger = logging.getLogger(__name__)

CERT_DATE_FORMAT = '%m %d %H:%M:%S %Y GMT'


def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for i in xrange(20))


class AttachmentSign(osv.Model):
    '''
        Support Model for Digital Signature
    '''
    _name = 'ir.attachment.sign'
    _description = 'Digital Signature Support Table'

    _columns = {
        'name': fields.char(
            'Token',
            size=20,
            required=True),
        'sha1': fields.char(
            'SHA1',
            size=60,
            required=True),
        'user_id': fields.many2one(
            'res.users',
            'Signer',
            required=True),
        'date_req': fields.datetime(
            'Date of Sign Request',
            required=True),
        'origin_id': fields.many2one(
            'ir.attachment',
            'Origin',
            required=True),
        'res_id': fields.related(
            'origin_id',
            'res_id',
            type="char",
            string='Resource Model',
            readonly=True),
        'res_model': fields.related(
            'origin_id',
            'res_model',
            type="integer",
            string='Resource ID',
            readonly=True),
        'parent_id': fields.related(
            'origin_id',
            'parent_id',
            type='many2one',
            relation='document.directory',
            string='Directory',
            readonly=True),
        'trigger': fields.boolean('Trigger Event'),
        'signed': fields.boolean('Signed'),
    }

    def _get_pem_params(self, cr, uid, certificate, context=None):
        pem = ""
        is_pem = False
        dstart = ''
        dend = ''
        for line in certificate.readlines():
            if 'Not Before' in line:
                not_before = line.split(': ')[1].\
                    replace('\n', '').strip()
                date_start = datetime.strptime(
                    self._convert_month(not_before),
                    CERT_DATE_FORMAT
                )
                dstart = date_start.strftime(
                    DEFAULT_SERVER_DATE_FORMAT)
            elif 'Not After' in line:
                not_after = line.split(': ')[1].\
                    replace('\n', '').strip()
                date_end = datetime.strptime(
                    self._convert_month(not_after),
                    CERT_DATE_FORMAT
                )
                dend = date_end.strftime(
                    DEFAULT_SERVER_DATE_FORMAT)
            elif '-----BEGIN CERTIFICATE-----' in line:
                pem += line
                is_pem = True
            elif '-----END CERTIFICATE-----' in line:
                pem += line
                is_pem = False
            else:
                if is_pem:
                    pem += line
        return pem, dstart, dend

    def _verify_der(self, cr, uid, filename_in, sid, context={}):
        user_obj = self.pool.get('res.users')
        verify_arguments = ('openssl',
                            'pkcs7',
                            '-inform',
                            'DER',
                            '-in',
                            filename_in,
                            '-print_certs',
                            '-text',
                            '-out',
                            filename_in + '.txt')
        ret_verify = subprocess.call(verify_arguments)
        with open(filename_in + '.txt', 'r') as certificate:
            pem, dstart, dend = self._get_pem_params(
                cr,
                uid,
                certificate,
                context=context
            )
            if sid.pem and sid.pem == pem:
                _logger.info('PEM verified!')
                certificate.close()
                user_obj.update_user_pem_line(
                    cr,
                    uid,
                    pem,
                    dstart,
                    dend,
                    user_id=sid.id,
                    context=context
                )
                user_obj.write(
                    cr,
                    SUPERUSER_ID,
                    sid.id,
                    {'pem': False},
                    context=context
                )
                return True
            elif sid.user_pem_ids:
                for user_pem in sid.user_pem_ids:
                    if user_pem.date_start <= fields.date.today() \
                            <= user_pem.date_end and \
                            user_pem.pem in pem:
                        certificate.close()
                        _logger.info('External PEM verified!')
                        return True
        certificate.close()
        os.remove(filename_in + '.txt')
        _logger.info('PEM not verified!')
        return False

    def _verify_sha1(self, cr, uid,
                     filename_in, filename_out,
                     tosign, context={}):
        verify_arguments = ('openssl',
                            'smime',
                            '-decrypt',
                            '-verify',
                            '-inform',
                            'DER',
                            '-in',
                            filename_in,
                            '-noverify',
                            '-out',
                            filename_out)
        ret_verify = subprocess.call(verify_arguments)
        _logger.info('OPENSSL return verify: ' + str(ret_verify))
        with open(filename_out) as to_verify:
            _sha1 = hashlib.sha1(to_verify.read()).hexdigest()
            _logger.info('sha1 verify: ' + _sha1)
            for elem in tosign:
                if elem.sha1 == _sha1 and \
                        self._verify_der(
                            cr, uid,
                            filename_in,
                            elem.user_id,
                            context):
                    to_verify.close()
                    return elem
            to_verify.close()
            return False

    def verify_signed(self, cr, uid, token=None, zfile=None, context=None):
        # FIXME: use verify single signed to check pem validity
        if not context:
            context = {}
        if not token:
            return _('Token not valid!')
        if not zfile:
            return _('File Zip not valid!')
        queue = self.search(
            cr,
            uid,
            [('name', '=', token),
             ('signed', '=', False)],
            context=context)
        if not queue:
            return _('No active signature requests for this token!')
        attachment_obj = self.pool.get('ir.attachment')
        tosign = self.browse(cr, uid, queue, context=context)
        # Creates Temporary File
        result = ''
        with tempfile.NamedTemporaryFile(prefix='tos_' +
                                         token,
                                         suffix='.zip', delete=False) as tmp:
            tmp.write(zfile.decode('base64'))
            tdir = tempfile.mkdtemp(prefix='tos_')
            with zipfile.ZipFile(tmp, 'r', zipfile.ZIP_DEFLATED) as archive:
                archive.extractall(tdir)
                for tname in archive.namelist():
                    if not tname.split('.')[-1:][0] == 'p7m':
                        # FIXME: raise exception
                        raise Exception
                    tpath_in = os.path.join(tdir, tname)
                    tpath_out = os.path.join(
                        tdir, '.'.join(tname.split('.')[:-1])
                    )
                    verified = self._verify_sha1(
                        cr, uid,
                        tpath_in, tpath_out,
                        tosign,
                        context=context)
                    if verified:
                        with open(tpath_in) as signed_file:
                            signed_attach = attachment_obj.create(
                                cr,
                                verified.user_id.id,
                                {
                                    'name': tname,
                                    'store_fname': tname,
                                    'datas': signed_file.read().
                                    encode('base64'),
                                    'datas_fname': tname,
                                    'parent_id': verified.origin_id.
                                    parent_id and verified.origin_id.
                                    parent_id.id or False,
                                    'res_model': verified.origin_id.res_model
                                    or False,
                                    'res_id': verified.origin_id.res_id
                                    or False,
                                },
                                context=context
                                )
                            signed_file.close()
                        attachment_obj.write(
                            cr,
                            verified.user_id.id,
                            verified.origin_id.id,
                            {
                                'to_sign': False,
                                'signed': signed_attach
                            },
                            context=context
                        )
                        self.write(cr, uid, verified.id,
                                   {'signed': True},
                                   context=context)
                        result = 'OK'
                    else:
                        result = 'Errore nella firma del documento!'
                archive.close()
                tmp.close()
                os.remove(tmp.name)
                shutil.rmtree(tdir)
        return result

    def verify_single_signed(self, cr, uid,
                             origin_id,
                             res_model=None, res_id=None,
                             data=None, context=None):
        if not context:
            context = {}
        if not data:
            return _('File not valid!')
        active_request_id = self.search(
            cr,
            uid,
            [('origin_id', '=', origin_id),
             ('user_id', '=', uid),
             ('res_model', '=', res_model),
             ('res_id', '=', res_id),
             ('signed', '=', False)],
            context=context)
        if not active_request_id:
            raise osv.except_osv(
                _('Error!'),
                _('No attachment to sign!')
            )
        attachment_obj = self.pool.get('ir.attachment')
        tosign = self.browse(cr, uid, active_request_id, context=context)
        # Creates Temporary File
        result = ''
        with tempfile.NamedTemporaryFile(suffix='.p7m',
                                         delete=False) as tmp:
            tmp.write(data.decode('base64'))
            tpath_in = tmp.name
            tmp.close()
        tpath_out = '.'.join(tpath_in.split('.')[:-1])
        verified = self._verify_sha1(
            cr, uid,
            tpath_in, tpath_out,
            tosign,
            context=context)
        if verified:
            with open(tpath_in) as signed_file:
                signed_attach = attachment_obj.create(
                    cr,
                    verified.user_id.id,
                    {
                        'name': tosign[0].origin_id.name + '.p7m',
                        'store_fname': tosign[0].origin_id.name + '.p7m',
                        'datas': signed_file.read().
                        encode('base64'),
                        'datas_fname': tosign[0].origin_id.name + '.p7m',
                        'parent_id': verified.origin_id.
                        parent_id and verified.origin_id.
                        parent_id.id or False,
                        'res_model': verified.origin_id.res_model
                        or False,
                        'res_id': verified.origin_id.res_id
                        or False,
                    },
                    context=context
                    )
                signed_file.close()
            attachment_obj.write(
                cr,
                verified.user_id.id,
                verified.origin_id.id,
                {
                    'to_sign': False,
                    'signed': signed_attach
                },
                context=context
            )
            self.write(cr, uid, verified.id,
                       {'signed': True},
                       context=context)
            result = 'OK'
        else:
            result = 'Errore nella firma del documento!'
            # FIXME: remove temporary file and folder
        return result

    def _convert_month(self, date_str):
        # FIXME: use safe thread locale in strptime
        months = {
            'Jan': '01',
            'Feb': '02',
            'Mar': '03',
            'Apr': '04',
            'May': '05',
            'Jun': '06',
            'Jul': '07',
            'Aug': '08',
            'Sep': '09',
            'Oct': '10',
            'Nov': '11',
            'Dec': '12'
        }
        month = date_str[:3]
        return date_str.replace(month, months[month])

    def set_pem(self, cr, uid, name, data, context=None):
        if not context:
            context = {}
        if not name.endswith('.p7m'):
                raise osv.except_osv(
                    _('Warning!'),
                    _('You can load only a .p7m file!'))
        user_obj = self.pool.get('res.users')
        with tempfile.NamedTemporaryFile(
                prefix='pem_',
                suffix='.p7m',
                delete=False) as tmp:
            tmp.write(data)
            filename_in = tmp.name
            tmp.close()
        verify_arguments = ('openssl',
                            'pkcs7',
                            '-inform',
                            'DER',
                            '-in',
                            filename_in,
                            '-print_certs',
                            '-text',
                            '-out',
                            filename_in + '.txt')
        ret_verify = subprocess.call(verify_arguments)
        with open(filename_in + '.txt', 'r') as certificate:
            pem, dstart, dend = self._get_pem_params(
                cr,
                uid,
                certificate,
                context=context
            )
            certificate.close()
        os.remove(filename_in)
        os.remove(filename_in + '.txt')
        return user_obj.update_user_pem_line(
            cr, uid, pem, dstart, dend, context=context
        )

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(AttachmentSign, self).write(
            cr, uid, ids, vals, context=context
            )
        for attachment_sign_id in ids:
            signer = self.browse(cr, uid, attachment_sign_id, context=context)
            if 'signed' in vals and signer.trigger:
                wf_service = netsvc.LocalService("workflow")
                _logger.info('workflow: attachment signed trigger')
                wf_service.trg_trigger(signer.user_id.id, 'ir.attachment',
                                       signer.origin_id.id, cr)
        return res


class Attachment(osv.Model):
    _inherit = 'ir.attachment'

    # TODO: modify structure to enable users to sign the same attachment.
    _columns = {
        'to_sign': fields.boolean('To Sign'),
        'signed': fields.many2one(
            'ir.attachment',
            'Signed Attachment',
            readonly=True),
    }

    def prepare_for_signature(self, cr, uid, ids,
                              context=None,
                              trigger=False):
        if not context:
            context = {}
        sign_model = self.pool.get('ir.attachment.sign')
        attach_model = self.pool.get('ir.attachment')
        # TODO: insert ir.attachment.sign security access
        queue = sign_model.search(
            cr,
            uid,
            [('user_id', '=', uid),
             ('signed', '=', False)],
            context=context)
        if queue:
            first_to_sign = sign_model.browse(
                cr, uid, queue[0], context=context
            )
            token = first_to_sign.name
            date_req = first_to_sign.date_req
        else:
            token = random_token()
            date_req = fields.datetime.now()
        for attachment in self.browse(cr, uid, ids, context=context):
            if not attachment.store_fname:
                raise osv.except_osv(
                    _('Error!'),
                    _('You must select a stored attachment!')
                )
            if not attachment.res_id and not attachment.parent_id:
                raise osv.except_osv(
                    _('Error!'),
                    _('You must select an attachment'
                      'related to a model or to a folder!')
                )
            vals = {
                'name': token,
                'sha1': attachment.store_fname.split('/')[1],
                'user_id': uid,
                'date_req': date_req,
                'trigger': trigger,
                'origin_id': attachment.id,
            }
            sign_model.create(cr, SUPERUSER_ID, vals, context=context)
            attach_model.write(
                cr,
                uid,
                attachment.id,
                {'to_sign': True},
                context=context)
        return True

    def unselect_for_signature(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        sign_model = self.pool.get('ir.attachment.sign')
        attach_model = self.pool.get('ir.attachment')
        queue = sign_model.search(
            cr,
            uid,
            [('user_id', '=', uid),
             ('origin_id', 'in', ids),
             ('signed', '=', False)],
            context=context)
        for verify_queue in sign_model.browse(cr, uid, queue, context=context):
            if verify_queue.trigger:
                raise osv.except_osv(
                    _('Permission Denied!'),
                    _('The attachment is related to a workflow!')
                )
        sign_model.unlink(cr, SUPERUSER_ID, queue, context=context)
        for attachment_id in ids:
            attach_model.write(
                cr,
                uid,
                attachment_id,
                {'to_sign': False},
                context=context)

    def is_signed(self, cr, uid, ids, context=None):
        if not ids:
            return False
        attachment = self.browse(cr, uid, ids[0], context=context)
        if attachment.signed:
            return True
        return False
