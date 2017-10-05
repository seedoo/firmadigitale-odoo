# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import logging
import werkzeug

import openerp
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class WebSignature(openerp.addons.web.http.Controller):
    _cp_path = '/sign'

    @openerp.addons.web.http.httprequest
    def set_signature(self, request, *args, **kw):
        _logger.info("set_signature")
        qcontext = request.params.copy()
        if not qcontext.get('token') or not \
                qcontext.get('dbname') or not \
                qcontext.get('zfile'):
            raise werkzeug.exceptions.NotFound()
        token = qcontext.get('token')
        dbname = qcontext.get('dbname')
        zfile = qcontext.get('zfile')
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                registry = RegistryManager.get(dbname)
                attachment_sign_obj = registry.get(
                    'ir.attachment.sign'
                )
                with registry.cursor() as cr:
                    res = attachment_sign_obj.verify_signed(
                        cr,
                        SUPERUSER_ID,
                        token=token,
                        zfile=zfile)
                    if res != "Ok":
                        qcontext['error'] = res
                        return request.make_response(
                            'Error: ' + res)
            except Exception, e:
                _logger.exception(e.message)
                qcontext['error'] = _('We can not process your request!')
                return request.make_response(
                    'Error: ' +
                    openerp.tools.exception_to_unicode(e))
        # FIXME: add the right return pattern
        return request.make_response('Ok')

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
