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


    def product_id_validation(self,product_list=False):
        Product_missing_list =[]
        Product_available_list =[]

        for i in product_list:
            product_template_id = request.env["product.template"].sudo().search([('active','=',True),('id','=',i.get('product_id'))])
            if not product_template_id:Product_missing_list.append(i.get('product_id'))
            if product_template_id:
                product_id = request.env["product.product"].sudo().search([('active','=',True),('product_tmpl_id','=',product_template_id.id)])
                Product_available_list.append({'product_id':product_id.id,'qty':i.get('product_qty')})

        if Product_missing_list:
            return Product_missing_list,True
        else:
            return Product_available_list,False
      
    @http.route('/create_customer', type='json', auth='none', website=True)
    def create_customer(self, **kw):
        _logger.info("==============================================>Entering Customer Creation=========================================================>")
        if kw.get('name') and kw.get('mobile') and kw.get('moc_doc_id') and kw.get('type'):
            if kw.get('type') not in ('partner_type','ven'):
                _logger.info("Type Not In Cus Or Ven==============================================>" + str(kw.get('type')))
                return {'Staus': 506,'Reason':'Type Not In Cus Or Ven.'}

            if not self.customer_mobile_validation(mobile_no=kw.get('mobile')):
                _logger.info("Mobile No Already Exist==============================================>")
                return {'Staus': 501,'Reason':'Mobile No Already Exist.'}

            if not self.customer_moc_doc_id_validation(moc_doc_id=kw.get('moc_doc_id')):
                _logger.info("Moc Doc Id  Already Exist==============================================>")
                return {'Staus': 504,'Reason':'Moc Doc Id  Already Exist.'}
            try:
                customer_rank = supplier_rank = 0

                if kw.get('type') == 'cus':  
                    customer_rank = 1
                else:
                    supplier_rank = 1

                partner_id = request.env["res.partner"].with_user(2).with_context(
                   {'lang': 'en_US', 
                    'uid': 2, 
                    'allowed_company_ids': [1], 
                    'search_default_customer': 1, 
                    'res_partner_search_mode': 'customer', 
                    'default_is_company': True, 
                    'default_customer_rank': customer_rank,
                    'default_supplier_rank': supplier_rank
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
            return {'Staus': 500,'Reason':'Name or Mobile or Moc Doc Id or Type Is Missing'}


    @http.route('/customer_update', type='json', auth='none', website=True)
    def customer_update(self, **kw):
        _logger.info("==============================================>Entering Customer Updation===============>" + str(kw))
        if kw.get('customer_id'):
            partner_id = self.search_customer_id_validation(customer_id=kw.get('customer_id'))
            if not partner_id:
                _logger.info("ID Does not Exist in odoo==============================================>")
                return {'Staus': 505,'Reason':'ID Doesnot Exist in Odoo, The customer May Be archieved or deleted'}

            _logger.info("Partner ID To Update==============================================> " + str(partner_id))
            update_list =[]
            try:
                if kw.get('name'):
                    update_list.append(kw.get('name'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).name = kw.get('name')
                if kw.get('street'):
                    update_list.append(kw.get('street'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).street = kw.get('street')
                if kw.get('street2'):
                    update_list.append(kw.get('street2'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).street2 = kw.get('street2')
                if kw.get('city'):
                    update_list.append(kw.get('city'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).city = kw.get('city')
                if kw.get('mobile'):
                    update_list.append(kw.get('mobile'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).mobile = kw.get('mobile')
                if kw.get('country_id'):
                    country_id = self.get_country_id(kw.get('country_id'))
                    if country_id:
                        update_list.append(country_id.name)
                        partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).country_id = country_id
                partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).write_api_values = kw
                if update_list:
                    return {'Staus': 200,'Status':'Successfully Updated'+'-'+str(update_list)}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("Customer Id Is Missing==============================================>")
            return {'Staus': 500,'Reason':'Customer Id Is Missing'}


    @http.route('/create_product_template', type='json', auth='none', website=True)
    def create_product_template(self, **kw):
        _logger.info("==============================================>Entering Product Creation===============>" + str(kw))
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
                            'taxes_id': [(6, 0, self.get_tax_ids(kw.get('customer_taxes_id'),tax_type='sales'))],
                            'supplier_tax_id': [(6, 0, self.get_tax_ids(kw.get('vendor_taxes_id'),tax_type='purchase'))],
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


    @http.route('/create_sale_order', type='json', auth='none', website=True)
    def create_sale_order(self, **kw):
        if kw.get('customer_id') and kw.get('product_list'):
            try:
                partner_id = self.search_customer_id_validation(kw.get('customer_id'))
                product_id = self.product_id_validation(product_list=kw.get('product_list'))
                if not partner_id:
                    _logger.info("Partner ID Does not Exist in odoo==============================================>")
                    return {'Staus': 705,'Reason':'Partner ID Doesnot Exist in Odoo, The Patient May Be archieved or deleted'}
                if product_id[1]:
                    _logger.info("Product ID Does not Exist in odoo==============================================>" + str(product_id))
                    return {'Staus': 706,'Reason':'Product ID Doesnot Exist in Odoo, The product May Be archieved or deleted' + str(product_id)}

                sale_order_id = request.env["sale.order"].with_user(2).create(
                        {
                            'partner_id': partner_id.id,
                        })
                if sale_order_id:
                    _logger.info("Sale Order Created==============================================> " + str(sale_order_id))
                    for i in product_id[0]:
                        sale_order_line_id = request.env["sale.order.line"].with_user(2).create(
                            {
                                'product_id': i.get('product_id'),
                                'order_id':sale_order_id.id,
                                'product_uom_qty':i.get('qty'),
                                'create_api_values':kw
                            })
                        _logger.info("Sale Order Line Created==============================================> " + str(sale_order_line_id))

                    sale_order_id.sudo().action_confirm()

                    return {'Staus': 200,'record_id':sale_order_id.id}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("partner_id or product_list Is Missing==============================================>")
            return{'Staus': 700,'Reason':'customer_id or product_list Is Missing'}



    @http.route('/create_purchase_order', type='json', auth='none', website=True)
    def create_purchase_order(self, **kw):
        if kw.get('customer_id') and kw.get('product_list'):
            try:
                partner_id = self.search_customer_id_validation(kw.get('customer_id'))
                product_id = self.product_id_validation(product_list=kw.get('product_list'))

                if not partner_id:
                    _logger.info("Partner ID Does not Exist in odoo==============================================>")
                    return {'Staus': 805,'Reason':'Partner ID Doesnot Exist in Odoo, The Patient May Be archieved or deleted'}
                if product_id[1]:
                    _logger.info("Product ID Does not Exist in odoo==============================================>" + str(product_id))
                    return {'Staus': 806,'Reason':'Product ID Doesnot Exist in Odoo, The product May Be archieved or deleted' + str(product_id)}

                purchase_order_id = request.env["purchase.order"].with_user(2).create(
                        {
                            'partner_id': partner_id.id,
                        })
                if purchase_order_id:
                    _logger.info("Purchase Order Created==============================================> " + str(purchase_order_id))
                    for i in product_id[0]:
                        purchase_order_line_id = request.env["purchase.order.line"].with_user(2).create(
                            {
                                'product_id': i.get('product_id'),
                                'order_id':purchase_order_id.id,
                                'product_qty':i.get('qty')
                            })
                        _logger.info("Purchase Order Line Created==============================================> " + str(purchase_order_line_id))

                    purchase_order_id.sudo().button_confirm()

                    # picking_id = request.env["stock.picking"].with_user(2).search([('origin','=',purchase_order_id.name)])

                    # picking_id.action_set_quantities_to_reservation()
                    # picking_id.button_validate()

                    return {'Staus': 200,'record_id':purchase_order_id.id}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        # else:
        #     _logger.info("partner_id or product_list Is Missing==============================================>")
        #     return{'Staus': 800,'Reason':'customer_id or product_list Is Missing'}

