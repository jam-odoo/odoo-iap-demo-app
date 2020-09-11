# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import requests
from odoo import http
from odoo.http import request
from odoo.addons.iap.tools import iap_tools


class CurExController(http.Controller):

    @http.route('/curex/v1/convert', type='json', auth="none", methods=['POST'], csrf=False)
    def curex_convert(self, user_token, request_res_id, from_cur, to_cur, credit=1, **kwargs):
        service_key = request.env['ir.config_parameter'].sudo().get_param('iap.curex_live.service_key')
        exchangerate_base = 'https://api.exchangerate.host/convert'
        request_record = request.env['iap.cur.ex.request'].sudo().create({
                                            'cur_ex_request_id': request_res_id,
                                            'from_cur': from_cur,
                                            'to_cur': to_cur,
                                            'credit': credit,
                                        })
        # IAP Authorize, get result and do callback
        with iap_tools.iap_charge(request.env, service_key, user_token, credit):
            params = { 'from': from_cur, 'to': to_cur }
            response = requests.get(exchangerate_base, params=params)
            response_data = response.json()
            request_record.sudo().write({'state': 'done', 'curex_rate':  response_data.get('result', 0)})
            response_data['cur_ex_request_id'] = request_record.id
        return response_data


    @http.route('/curex/v1/request', type='json', auth="none", methods=['POST'], csrf=False)
    def curex_request(self, user_token, request_res_id, from_cur, to_cur, credit=1, **kwargs):
        service_key = request.env['ir.config_parameter'].sudo().get_param('iap.curex_live.service_key')
        description = 'Authorizing credit %f for currency exchange request '
                        'from %s to %s for doucment %s'%(credit, from_cur, to_cur, request_res_id)
        print (request.env, service_key, user_token, credit, description)
        #Authorize the transaction using user account
        transection_token = iap_tools.iap_authorize(request.env, service_key, user_token, credit, description=description)
        #Record request details and Token for later usr
        request_record = request.env['iap.cur.ex.request'].sudo().create({
                                        'cur_ex_request_id': request_res_id,
                                        'credit_auth_token': transection_token,
                                        'from_cur': from_cur,
                                        'to_cur': to_cur,
                                        'credit': credit,
                                        'description': description,
                                    })
        response = {
            'cur_ex_request_id': request_record.id,
            'credit_auth_token': transection_token
        }
        return json.dumps(response)



    @http.route('/curex/v1/fetch', type='json', auth="none", methods=['POST'], csrf=False)
    def curex_update(self, user_token, request_id, credit_auth_token, **kwargs):
        service_key = request.env['ir.config_parameter'].sudo().get_param('iap.curex_live.service_key')
        request_record = request.env['iap.cur.ex.request'].sudo().search([
                                    ('credit_auth_token', '=', credit_auth_token),
                                    ('id', '=', request_id)
                                ], limit=1)
        return_data = {'result': False}
        if not request_record:
            return_data.update({'error': 'We could not find requested record, please write us at missing@yourcompnay.com'})
            return json.dumps(return_data)
        transection_token = request_record.credit_auth_token
        try:
            if request_record.state in ('todo', 'cancel'):
                request_record.get_ex_rate()
            return_data.update({'result': request_record.curex_rate})
        except Exception as ex:
            #Cnacel the authorized transection assuming failure and we can't provider service
            iap_tools.iap_cancel(request.env, transection_token, service_key)
            return_data.update({'error': 'Sorry, We could not process your request at moment, please try again later'})
            return json.dumps(return_data)
        # We have success and let charge the authorized transection
        iap_tools.iap_capture(request.env, transection_token, service_key, request_record.credit)
        return json.dumps(return_data)
