# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': ' IAP Currency Exchange Service',
    'category': 'Tools',
    'version': '1.0',
    'author': 'Odoo S.A.',
    'website': 'https://www.odoo.com/documentation/14.0/webservices/iap.html',
    'summary': 'IAP Accounting Currency Exchange Service Application',
    'description': """
IAP Accounting Currency Exchange Service Application
=======================================================
This is a sample client application to show Odoo In-App purchase functionality.
This shows IAP Service API and Odoo Helpers provoded for it
https://www.odoo.com/documentation/master/webservices/iap.html#odoo-helpers
- Charging
- Authorize
- Cancel
- Capture

This application is service application and can be called to get currency exchange
rates by providing twp currancies symbols'

This application is designed to work with Odoo IAP Sandbox only.
""",
    'depends': [
        'account',
        'iap',
    ],
    'data': [
        'views/account_move_views.xml'
    ],
    'application': False,
    'installable': True,
}