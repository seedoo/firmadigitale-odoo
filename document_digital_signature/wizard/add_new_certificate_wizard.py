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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class add_certificate(osv.osv_memory):
    _name = "document.ds.add.certificate"

    _columns = {
        'name': fields.char(
            'File Name',
            readonly=False,
            required=True
        ),
        'data': fields.binary(
            'File',
            required=True
        )
    }

    def set_pem(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        wizard = self.browse(cr, uid, ids[0], context=context)
        document_digital_signature_obj = self.pool.get('ir.attachment.sign')
        return document_digital_signature_obj.set_pem(
            cr,
            uid,
            wizard.name,
            wizard.data.decode('base64'),
            context=context
        )
