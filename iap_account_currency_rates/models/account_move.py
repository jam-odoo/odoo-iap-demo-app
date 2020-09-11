# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import models, fields, _
from odoo.addons.iap.tools import iap_tools
from odoo.exceptions import UserError


class AccountMoveIAP(models.Model):
    _inherit = 'account.move'

    _default_live_cur_ex_rate = 'http://localhost:9069'

    iap_curex_rate = fields.Monetary(string='Currency Exchange Rate', default=0.0, 
                                            copy=False, currency_field='company_currency_id')
    iap_curex_rate_dt = fields.Datetime(string='Exchange Request Date', copy=False)
    iap_curex_request_id = fields.Char(string='IAP Request ID', readonly=True, copy=False)
    iap_curex_request_hold_token = fields.Char(string='IAP Request Hold Token',
                                        readonly=True, copy=False)

    def fetch_cur_rate(self):
        user_token = self.env['iap.account'].get('live_cur_ex_rate')
        service_endpoint = self.env['ir.config_parameter'].sudo().get_param('live_cur_ex_rate.endpoint', self._default_live_cur_ex_rate)
        for move in self:
            if move.company_currency_id == move.currency_id:
                raise UserError(_('Invoice currency and compnay currency is same, '
                                    'this doucment do not require exchange rates.'))

            params = {
                'user_token': user_token.account_token,
                'request_res_id': '%s,%s'%(move._name, move.id),
                'from_cur': move.company_currency_id.name,
                'to_cur': move.currency_id.name,
            }
            
            response = iap_tools.iap_jsonrpc(service_endpoint + '/curex/v1/convert', params=params)
            result = response.get('result', 0)
            if not result:
                raise UserError(_('Could not get the result please try again later. '
                                    'No credit was consuemed for this request.'))
            move.write({
                'iap_curex_rate': result,
                'iap_curex_rate_dt': fields.Datetime.now(),
            })
            credit = self.env['iap.account'].get_credits('live_cur_ex_rate')
            credit_url = self.env['iap.account'].get_credits_url('live_cur_ex_rate')
            body = '''<p>
Updated exchange rate to <i>%f</i> from invoice currency <i>%s</i> to company currency <i>%s</i> using one IAP credit.<br/>
Reaming Credit balance is <i><a href=%s target="new"> %f </a></i>.
<br/><br/>Request technical details: <br/>
%s<br/></p>'''%(result, move.currency_id.name, move.company_currency_id.name, credit_url, credit, response)
            move.message_post(subject='IAP Currency Exchange Rate Request',body=body)
        return {'type': 'ir.actions.act_window_close'}

    def send_cerex_request(self):
        user_token = self.env['iap.account'].get('live_cur_ex_rate')
        service_endpoint = self.env['ir.config_parameter'].sudo().get_param('live_cur_ex_rate.endpoint', self._default_live_cur_ex_rate)
        for move in self:
            if move.company_currency_id == move.currency_id:
                raise UserError(_('Invoice currency and compnay currency is same, this doucment do not require exchange rates.'))
            params = {
                'user_token': user_token.account_token,
                'request_res_id': '%s,%s'%(move._name, move.id),
                'from_cur': move.company_currency_id.name,
                'to_cur': move.currency_id.name,
            }
            endpoint = self.env['ir.config_parameter'].sudo().get_param('live_cur_ex_rate.endpoint', self._default_live_cur_ex_rate)
            response = iap_tools.iap_jsonrpc(service_endpoint + '/curex/v1/request', params=params)
            response_data = json.loads(response)
            move.write({
                'iap_curex_request_id': response_data.get('cur_ex_request_id'),
                'iap_curex_request_hold_token': response_data.get('credit_auth_token'),
            })
            move.message_post(body='Exchange rate request has been succesfully sent.')
        return {'type': 'ir.actions.act_window_close'}

    def fetch_cerex_update(self):
        user_token = self.env['iap.account'].get('live_cur_ex_rate')
        service_endpoint = self.env['ir.config_parameter'].sudo().get_param('live_cur_ex_rate.endpoint', self._default_live_cur_ex_rate)


        for move in self:
            if not move.iap_curex_request_id or not move.iap_curex_request_hold_token:
                raise UserError(_('INvoice request is not genereated yet, please senf requets first'))
            params = {
                'user_token': user_token.account_token,
                'request_id': move.iap_curex_request_id,
                'credit_auth_token': move.iap_curex_request_hold_token,
            }
            endpoint = self.env['ir.config_parameter'].sudo().get_param('live_cur_ex_rate.endpoint', self._default_live_cur_ex_rate)
            response = iap_tools.iap_jsonrpc(service_endpoint + '/curex/v1/fetch', params=params)
            response_data = json.loads(response)
            if response_data.get('error', False):
                raise UserError(response_data.get('error', ''))
            move.write({
                'iap_curex_request_id': False,
                'iap_curex_request_hold_token': False,
                'iap_curex_rate': response_data.get('result'),
                'iap_curex_rate_dt': fields.Datetime.now(),
            })
        return {'type': 'ir.actions.act_window_close'}
