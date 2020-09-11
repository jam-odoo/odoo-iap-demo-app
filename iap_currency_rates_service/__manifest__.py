# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': ' IAP Invoices Currency Exchange Service',
    'category': 'Accounting/Tools',
    'version': '1.0',
    'author': 'Odoo S.A.',
    'website': 'https://www.odoo.com/documentation/14.0/webservices/iap.html',
    'summary': 'IAP Accounting Currency Exchange Client Application',
    'description': """
IAP Accounting Currency Exchange Client Application
=======================================================
This is a sample client application to show Odoo In-App purchase functionality.
This application will allow users to pull the currency exchange rate on 
invoices where company currency and invoice currency is different.
This application is designed to work with Odoo IAP Sandbox only.
""",
    'depends': [
        'web',
        'iap',
    ],
    'data': [
        'data/ir.model.access.csv',
        'data/iap_ir_config_param_data.xml',
        'views/curex_service_views.xml',
    ],
    'application': False,
    'installable': True,
}