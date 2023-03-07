# -*- coding: utf-8 -*-

# import werkzeug
from odoo import http
from odoo.http import request
import logging, requests
_logger = logging.getLogger(__name__)
# from requests_oauthlib import OAuth2Session

class Authorize2(http.Controller):
    @http.route('/auth', type='json', auth='none', website=True)
    def get_authorized_url(self, **kw):
        _logger.info("Api Status=====================(Success)====================================> {x}".format(x=str(kw)))
        if kw.get('partner_id'):
            invoice_id = request.env["sale.order"].sudo().create({
                'partner_id': 1602, 
                # 'partner_invoice_id': 1602, 
                # 'partner_shipping_id': 1602, 
                # 'sale_order_template_id': False, 
                # 'validity_date': False, 
                # 'date_order': '2023-03-07 04:32:21', 
                # 'show_update_pricelist': False, 
                # 'pricelist_id': 1, 
                # 'payment_term_id': False, 
                # 'order_line': [], 'note': '<p><br></p>', 
                # 'sale_order_option_ids': [], 
                # 'user_id': 2, 
                # 'team_id': 1, 
                'company_id': 1, 
                # 'require_signature': True, 
                # 'require_payment': False, 
                # 'client_order_ref': False, 
                # 'tag_ids': [[6, False, []]], 
                # 'fiscal_position_id': False, 
                # 'analytic_account_id': False, 
                # 'warehouse_id': 1, 
                # 'incoterm': False, 
                # 'picking_policy': 'direct', 
                # 'commitment_date': False, 
                # 'origin': False, 
                # 'campaign_id': False, 
                # 'medium_id': False, 
                # 'source_id': False, 
                # 'signed_by': False, 
                # 'signed_on': False, 
                # 'signature': False, 
                # '__last_update': False, 
                # 'message_follower_ids': [], 
                # 'activity_ids': [], 
                # 'message_ids': []
                })
            print(invoice_id,'111111111111111111111111111111111111111111111111111')
            return{'Success': 200}
        # res = request.env['qb.backend'].sudo().search([])
        # res.write({
        #     'company_id': realmId,
        #     'o2_auth_url': res.redirect_uri + '?' + 'state=%s' % state + '&code=%s' % code + '&realmId=%s' % realmId,
        # })
        # context = {
        #     'id': str(res.id),
        #     'client_key': str(res.client_key),
        #     'client_secret': str(res.client_secret),
        #     'company_id': str(res.company_id),
        #     'redirect_uri': str(res.redirect_uri),
        #     'o2_auth_url': str(res.o2_auth_url),
        #     'token_url': str(res.token_url),
        #     'location': str(res.location),
        #     'scope': str(res.scope)
        # }
        # res.qb_auth_o2_auto_step2(context)
        # return werkzeug.utils.redirect('/')