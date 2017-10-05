# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (c) 2004-2012 OpenERP S.A. <http://openerp.com>
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

import base64

from openerp import tools
from openerp.osv import fields,osv
from openerp.tools.translate import _
from openerp.tools.misc import get_iso_codes

from urlparse import urlparse

from ..helper.zip_helper import InMemoryZip

NEW_LANG_KEY = '__new__'


class export_tos(osv.osv_memory):
    _name = "document.ds.export.single.tos"

    _columns = {
        'name': fields.char('File Name', readonly=True),
        'data': fields.binary('File', readonly=True),
        'state': fields.selection([('choose', 'choose'),
                                   ('get', 'get')])
    }

    def _default_name(self, cr, uid, context):
        attachment = self.pool.get('ir.attachment').browse(
            cr,
            uid,
            context['active_id'],
            context=context
            )
        return attachment.name + '.tos'

    _defaults = {
        'name': _default_name,
        'state': 'choose',
    }

    def get_tos(self, cr, uid, ids, context=None):
        if context is None or 'active_id' not in context:
            raise osv.except_osv(
                _('Error!'),
                _('No attachments to sign!')
            )
        wizard = self.browse(cr, uid, ids)[0]
        sign_model = self.pool.get('ir.attachment.sign')
        user_model = self.pool.get('res.users')
        sign_ids = sign_model.search(
            cr,
            uid,
            [('user_id', '=', uid),
             ('origin_id', '=', context['active_id']),
             ('signed', '=', False)]
        )
        if not sign_ids:
            raise osv.except_osv(
                _('Error!'),
                _('No attachments to sign!')
            )
        imz = InMemoryZip()
        # set server and db info
        config_param_obj = self.pool.get('ir.config_parameter')
        srv = config_param_obj.get_param(
            cr,
            uid,
            'server.ip.signature')
        if srv:
            imz.write_info([srv + ',' + cr.dbname + '\n'])
        else:
            raise osv.except_osv(
                _('Error!'),
                _('No server.ip.signature parameter found on system!')
            )
        current_user = user_model.browse(cr, uid, uid, context=context)
        reset = '\n'
        if current_user.reset_pem:
            reset = '--# Reset # --\n'
        for num, sign in enumerate(
                sign_model.browse(cr, uid, sign_ids, context=context)
                ):
            if not num:
                imz.write_info([sign.name + '\n',
                                reset,
                                '--# Info #--\n'])
            attachment = sign.origin_id
            imz.append(attachment.datas_fname,
                       attachment.datas.decode('base64'))
            # TODO: to improve with a new field in ir_attachment_sign
            resign = 'false'
            if attachment.datas_fname:
                storedfilename = attachment.datas_fname
            else:
                storedfilename = attachment.name
            if storedfilename.endswith('.p7m'):
                resign = 'true'
            imz.write_info(
                [storedfilename +
                 ',' +
                 sign.date_req +
                 ',' +
                 resign + '\n']
            )
        imz.append("INFO", imz.get_info())
        self.write(cr, uid, ids,
                   {'state': 'get',
                    'data': imz.read().encode('base64'),
                    'name': wizard.name},
                   context=context)
        imz.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'document.ds.export.single.tos',
            'view_mode': 'form_document_wait_sign',
            'view_type': 'form',
            'res_id': wizard.id,
            'context': {'attachment_id': attachment.id},
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
