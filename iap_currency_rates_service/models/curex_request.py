# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import requests
from odoo import models, fields, _


class IdRequest(models.Model):
    _name = 'iap.cur.ex.request'
    _rec_name = 'id'
    _description = 'IAP Currency Requests'
    
    cur_ex_request_id = fields.Char(string='Request Document')
    credit_auth_token = fields.Char(string='Credit Authorization TOken')
    credit = fields.Float(string='Credit Charge')
    from_cur = fields.Char(string='Form Currency Code')
    to_cur = fields.Char(string='To Currency Code')
    curex_rate = fields.Float(string='Exchange Rate', digits=(12,6))
    description = fields.Text(string='Description')
    state = fields.Selection(selection=[
                        ('todo', 'Todo'),
                        ('updated', 'Rate Updated'),
                        ('done', 'Charged'),
                        ('cancel', 'Cancelled')], default='todo')

    def get_ex_rate(self):
        exchangerate_base = 'https://api.exchangerate.host/convert'
        for record in self:
            params = { 'from': record.from_cur, 'to': record.to_cur }
            response = requests.get(exchangerate_base, params=params)
            response_data = response.json()
            curex_rate = response_data.get('result', 0)
            if not curex_rate:
                continue
            record.write({
                'state': 'updated',
                'curex_rate': curex_rate,
            })