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

import logging

_logger = logging.getLogger(__name__)


_begin_pem = ''
_end_pem = ''


class UserPem(osv.Model):
    _name = 'res.users.pem'
    _description = 'External PEM list for the user'
    _order = 'date_start DESC'
    _rec_name = 'date_start'

    _columns = {
        'date_start': fields.date(
            'Date Start',
            required=True),
        'date_end': fields.date(
            'Date End',
            required=True),
        'pem': fields.text(
            'PEM Certificate',
            required=True),
        'user_id': fields.many2one(
            'res.users',
            'User',
            required=True
        )
    }


class User(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'pem': fields.text(
            'PEM Certificate'
        ),
        'user_pem_ids': fields.one2many(
            'res.users.pem',
            'user_id',
            string='PEMs',
        ),
        'reset_pem': fields.boolean(
            'Reset Pem Configuration'
        ),
    }

    _default = {
        'reset_pem': True,
    }

    def update_pem(self, cr, uid, pem, context=None):
        if not context:
            context = {}
        if not pem or \
                not pem.startswith(_begin_pem) or \
                not pem.endswith(_end_pem):
            return False
        user_obj = self.pool.get('res.users')
        user_obj.write(
            cr,
            SUPERUSER_ID,
            uid,
            {'pem': pem,
             'reset_pem': False},
            context=context
            )
        return True

    def update_user_pem_line(
            self, cr, uid, pem,
            dstart, dend,
            user_id=False, context=None
            ):
        if not user_id:
            user_id = uid
        user_pem_obj = self.pool.get('res.users.pem')
        if dend < fields.date.today():
            raise osv.except_osv(
                _('Warning!'),
                _('The Certificate is expired!'))
        if not pem:
            raise osv.except_osv(
                _('Warning!'),
                _('Wrong Certificate!'))
        user = self.browse(cr, SUPERUSER_ID, user_id, context=context)
        for certification in user.user_pem_ids:
            if pem == certification.pem:
                if dend <= certification.date_end:
                    _logger.warning(
                        'The PEM Certificate for %s is already loaded!'
                        % user.name)
                else:
                    user_pem_obj.write(
                        cr,
                        SUPERUSER_ID,
                        certification.id,
                        {
                            'date_start': dstart,
                            'date_end': dend
                        },
                        context=context
                    )
                    self.write(
                        cr,
                        SUPERUSER_ID,
                        user_id,
                        {'reset_pem': False},
                        context=context)
                    _logger.info('PEM updated for user %s' % user.name)
                return True
        user_pem_obj.create(
            cr,
            SUPERUSER_ID,
            {
                'user_id': user_id,
                'pem': pem,
                'date_start': dstart,
                'date_end': dend
            },
            context=context
        )
        self.write(
            cr,
            SUPERUSER_ID,
            user_id,
            {'reset_pem': False},
            context=context)
        _logger.info('PEM created for user %s' % user.name)

        return True
