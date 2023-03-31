# -*- coding: utf-8 -*-

# import werkzeug
from odoo import http
from odoo.http import request
import logging, requests
_logger = logging.getLogger(__name__)
from odoo import http, SUPERUSER_ID, _


# from requests_oauthlib import OAuth2Session

class Authorize2(http.Controller):

    def customer_mobile_validation(self,mobile_no=False):
        partner_id = request.env["res.partner"].sudo().search([('active','=',True),('mobile','=',mobile_no)])
        if partner_id:
            return False
        else:
            return True

    def customer_moc_doc_id_validation(self,moc_doc_id=False):
        partner_id = request.env["res.partner"].sudo().search([('active','=',True),('moc_doc_id','=',moc_doc_id)])
        if partner_id:
            return False
        else:
            return True

    def search_customer_id_validation(self,customer_id=False):
        partner_id = request.env["res.partner"].sudo().search([('active','=',True),('id','=',customer_id)])
        if partner_id:
            return partner_id
        else:
            return False

    def get_country_id(self,country_name=False):
        country_id = request.env["res.country"].sudo().search([('name','=',country_name)],limit =1)
        if country_id:
            return country_id.id
        else:
            return False

    def get_product_category(self,categ_name=False):
        product_categ_id = request.env["product.category"].sudo().search([('name','=',categ_name)],limit =1)
        if product_categ_id:
            return product_categ_id.id
        else:
            return 1

    def get_tax_ids(self,tax_ids=False,tax_type=''):
        if tax_ids:
            _logger.info("Tax_ids==============================================> " + str(tax_ids))
            tax_list = []
            for i in tax_ids:
                tax_id = request.env["account.tax"].sudo().search([('name','=',i),('type_tax_use','=',tax_type)],limit =1)
                if tax_id:tax_list.append(tax_id.id)
            _logger.info("Tax List==============================================> " + str(tax_list))
            return tax_list
        else:
            return []

    def product_internal_ref_validation(self,default_code=False):
        product_template_id = request.env["product.template"].sudo().search([('active','=',True),('default_code','=',default_code)])
        if product_template_id:
            return False
        else:
            return True
      
    @http.route('/create_customer', type='json', auth='none', website=True)
    def create_customer(self, **kw):
        _logger.info("==============================================>Entering Customer Creation=========================================================>")
        _logger.info("name=========================================================>"+ str(kw.get('name')))
        _logger.info("mobile=========================================================>"+ str(kw.get('mobile')))
        _logger.info("moc_doc_id=========================================================>"+ str(kw.get('moc_doc_id')))
        if kw.get('name') and kw.get('mobile') and kw.get('moc_doc_id'):
            if not self.customer_mobile_validation(mobile_no=kw.get('mobile')):
                _logger.info("Mobile No Already Exist==============================================>")
                return {'Staus': 501,'Reason':'Mobile No Already Exist.'}

            if not self.customer_moc_doc_id_validation(moc_doc_id=kw.get('moc_doc_id')):
                _logger.info("Moc Doc Id  Already Exist==============================================>")
                return {'Staus': 504,'Reason':'Moc Doc Id  Already Exist.'}
            try:
                partner_id = request.env["res.partner"].with_user(2).with_context(
                   {'lang': 'en_US', 
                    'uid': 2, 
                    'allowed_company_ids': [1], 
                    'search_default_customer': 1, 
                    'res_partner_search_mode': 'customer', 
                    'default_is_company': True, 
                    'default_customer_rank': 1
                    }).create({
                                'name': kw.get('name'), 
                                'company_id': 1, 
                                'street': kw.get('street'), 
                                'street2': kw.get('street2'),
                                'city': kw.get('city'), 
                                'mobile': kw.get('mobile'), 
                                'national_id': kw.get('national_id'), 
                                'country_id': self.get_country_id(kw.get('country_id')), 
                                'active': True, 
                                'moc_doc_id': kw.get('moc_doc_id'), 
                                'create_uid':2, 
                                'create_api_values': kw
                            })

                if partner_id:
                    _logger.info("Partner Created==============================================> " + str(partner_id))
                    return {'Staus': 200,'record_id':partner_id.id}
                else:
                     _logger.error("Customer Not Created==============================================>")
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("Name or Mobile or Moc Doc Id Is Missing==============================================>")
            return {'Staus': 500,'Reason':'Name or Mobile or Moc Doc Id Is Missing'}


    @http.route('/customer_update', type='json', auth='none', website=True)
    def customer_update(self, **kw):
        if kw.get('customer_id'):
            partner_id = self.search_customer_id_validation(customer_id=kw.get('customer_id'))
            if not partner_id:
                _logger.info("ID Does not Exist in odoo==============================================>")
                return {'Staus': 505,'Reason':'ID Doesnot Exist in Odoo, The customer May Be archieved or deleted'}

            _logger.info("Partner ID To Update==============================================> " + str(partner_id))
            count=0
            try:
                if kw.get('name'):
                    count+=1
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).name = kw.get('name')
                if kw.get('street'):
                    count+=1
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).street = kw.get('street')
                if kw.get('street2'):
                    count+=1
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).street2 = kw.get('street2')
                if kw.get('city'):
                    count+=1
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).city = kw.get('city')
                if kw.get('mobile'):
                    count+=1
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).mobile = kw.get('mobile')
                if kw.get('country_id'):
                    count+=1
                    country_id = self.get_country_id(kw.get('country_id'))
                    if country_id:
                        partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).country_id = country_id
                partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).write_api_values = kw
                if count >=1:
                    return {'Staus': 200,'Status':'Successfully Updated'}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("Customer Id Is Missing==============================================>")
            return{'Staus': 500,'Reason':'Customer Id Is Missing'}


    @http.route('/create_product_template', type='json', auth='none', website=True)
    def create_product_template(self, **kw):
        if kw.get('name') and kw.get('detailed_type') and kw.get('invoice_policy') and kw.get('list_price') and kw.get('standard_price') and kw.get('categ_id') and kw.get('default_code') and kw.get('purchase_method') and kw.get('sale_ok') and kw.get('purchase_ok'):
            if not self.product_internal_ref_validation(default_code=kw.get('default_code')):
                _logger.info("Internal Ref Already Exist==============================================>")
                return {'Staus': 601,'Reason':'Internal Ref Already Exist.'}
            try:
                product_template_id = request.env["product.template"].with_user(2).with_context(
                        {
                           'lang': 'en_US', 
                            'uid': 2, 
                            'allowed_company_ids': [1], 
                        }).create(
                        {
                            'name': kw.get('name'),
                            'detailed_type': kw.get('detailed_type'),
                            'invoice_policy': kw.get('invoice_policy'),
                            'list_price': kw.get('list_price'), 
                            'standard_price': kw.get('standard_price'),
                            'categ_id': self.get_product_category(kw.get('categ_id')),
                            'default_code': kw.get('default_code'),
                            'purchase_method': kw.get('purchase_method'),
                            'sale_ok': kw.get('sale_ok'),
                            'purchase_ok': kw.get('purchase_ok'),
                            'taxes_id': [(6, 0, self.get_tax_ids(kw.get('taxes_id'),tax_type='sales'))],
                            'supplier_tax_id': [(6, 0, self.get_tax_ids(kw.get('taxes_id'),tax_type='purchase'))],
                            'create_api_values': kw
                        })
                if product_template_id:
                    _logger.info("Product Created==============================================> " + str(product_template_id))
                    return {'Staus': 200,'record_id':product_template_id.id}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("name or detailed_type or invoice_policy or list_price or standard_price or categ_id or default_code or purchase_method or sale_ok or purchase_okd Is Missing==============================================>")
            return{'Staus': 600,'Reason':'name or detailed_type or invoice_policy or list_price or standard_price or categ_id or default_code or purchase_method or sale_ok or purchase_ok Is Missing'}
