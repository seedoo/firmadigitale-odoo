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

{
    'name': 'Firma Digitale',
    'version': '1.0',
    'author': 'Innoviu',
    'category': 'Document',
    'sequence': 10,
    'website': 'http://www.innoviu.com',
    'summary': 'Document Digital Sign',
    'description': """
Innoviu personalization for document module
================================================

This module adds the digital sign to attachments
    """,
    'author': 'Innoviu Srl',
    'website': 'http://www.innoviu.com',
    'depends': [
        'document',
    ],
    'data': [
        'security/document_digital_signature_security.xml',
        'security/ir.model.access.csv',
        'data/document_digital_signature_data.xml',
        'view/res_user_view.xml',
        'wizard/export_tos_view.xml',
        'wizard/export_tos_single_attachment_view.xml',
        'wizard/add_new_certificate_wizard_view.xml',
        'view/document_digital_signature_view.xml',
    ],
    'update_xml': [],
    'installable': True,
    'application': True,
    'active': False,
    'js': [
        'static/src/js/document_sign_wait.js',
    ],
    'qweb': [
        "static/src/xml/document_sign_wait.xml",
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
