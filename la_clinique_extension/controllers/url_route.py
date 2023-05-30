# -*- coding: utf-8 -*-

# import werkzeug
from odoo import http
from odoo.http import request
import logging, requests
_logger = logging.getLogger(__name__)
from odoo import http, SUPERUSER_ID, _


# from requests_oauthlib import OAuth2Session

class Authorize2(http.Controller):

    def customer_mobile_validation(self,mobile_no=False,customer_id=False):
        if customer_id:
            partner_id = request.env["res.partner"].sudo().search([('id','!=',customer_id),('active','=',True),('mobile','=',mobile_no)])
        else:
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

    def search_insurance_provider_id_validation(self,provider_id=False):
        provider_id = request.env["insurance.provider"].sudo().search([('active','=',True),('name','=',provider_id)],limit=1)
        if provider_id:
            return provider_id,True
        else:
            all_list = [i.name for i in request.env["insurance.provider"].sudo().search([('active','=',True)])]
            return all_list,False

    def search_currency_id_validation(self,currency_id=False):
        currency_id = request.env["res.currency"].sudo().search([('active','=',True),('name','=',currency_id)],limit=1)
        if currency_id:
            return currency_id
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
            return product_categ_id.id,True
        else:
            categ_list = [i.name for i in request.env["product.category"].sudo().search([])]
            return categ_list,False

    

    def get_uom_id(self,uom=False):
        if uom:
            _logger.info("Uom ==============================================> " + str(uom))
            uom_id = request.env["uom.uom"].sudo().search([('name','=',uom)],limit =1)
            if uom_id:
                return uom_id.id,True
            else:
                uom_list = [i.name for i in request.env["uom.uom"].sudo().search([])]
                return uom_list,False
        

    def product_internal_ref_validation(self,default_code=False):
        product_template_id = request.env["product.template"].sudo().search([('active','=',True),('default_code','=',default_code)])
        if product_template_id:
            return False
        else:
            return True


    def get_tax_ids(self,tax_ids=False,tax_type=''):
        _logger.info("Tax_ids==============================================> " + str(tax_ids))
        tax_list = []
        for i in tax_ids:
            tax_id = request.env["account.tax"].sudo().search([('name','=',i),('type_tax_use','=',tax_type)],limit =1)
            if tax_id:
                tax_list.append(tax_id.id)
            else:
                all_tax_list = [i.name for i in request.env["account.tax"].sudo().search([('type_tax_use','=',tax_type)])]
                return all_tax_list,False
        _logger.info("Tax List==============================================> " + str(tax_list))
        return tax_list,True



    def product_id_validation(self,product_list=False):
        Product_missing_list =[]
        Product_available_list =[]

        for i in product_list:
            tax_list = []
            product_template_id = request.env["product.template"].sudo().search([('active','=',True),('id','=',i.get('product_id'))])
            if not product_template_id:Product_missing_list.append(i.get('product_id'))
            if product_template_id:
                product_id = request.env["product.product"].sudo().search([('active','=',True),('product_tmpl_id','=',product_template_id.id)])
                if i.get('customer_tax'):
                    tax_list = self.get_tax_ids(i.get('customer_tax'),tax_type='sale')
                if i.get('vendor_tax'):
                    tax_list = self.get_tax_ids(i.get('vendor_tax'),tax_type='purchase')

                Product_available_list.append(
                    {
                        'product_id': product_id.id,
                        'qty': i.get('product_qty'),
                        'moc_doc_price_unit': i.get('moc_doc_price_unit'),
                        'tax_id': [(6, 0,tax_list[0])] if tax_list else [(6, 0,tax_list)],
                        'disc': i.get('disc') if i.get('disc') else 0.0,
                    })

        if Product_missing_list:
            return Product_missing_list,True
        else:
            return Product_available_list,False

    def check_price_validation(self,product_list=False):
        for i in product_list:
            if i.get('moc_doc_price_unit') < 0.1:
                return True
       

    def get_product_template_id(self,product=False):
        if product:
            product_template_id = request.env["product.template"].sudo().search([('active','=',True),('id','=',product)])
            if product_template_id:
                return product_template_id
            else:
                return False

    def search_pricleist(self):
        pricelist_id = request.env["product.pricelist"].sudo().search([('name','=','API Pricelist')])
        if pricelist_id:
            return pricelist_id
        else:
            False
      
    @http.route('/create_customer', type='json', auth='none', website=True)
    def create_customer(self, **kw):
        _logger.info("==============================================>Entering Customer Creation=========================================================>")
        if kw.get('name') and kw.get('mobile') and kw.get('moc_doc_id') and kw.get('type'):
            if kw.get('type') not in ('cus','ven'):
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
                    }).create({
                                'name': kw.get('name'), 
                                'company_id': 1, 
                                'street': kw.get('street'), 
                                'street2': kw.get('street2'),
                                'city': kw.get('city'), 
                                'email': kw.get('email'),
                                'mobile': kw.get('mobile'), 
                                'national_id': kw.get('national_id'), 
                                'country_id': self.get_country_id(kw.get('country_id')), 
                                'active': True, 
                                'moc_doc_id': kw.get('moc_doc_id'), 
                                'create_uid':2, 
                                'create_api_values': kw,
                                'customer_rank': customer_rank,
                                'supplier_rank': supplier_rank,
                                'is_company': True
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
                if kw.get('mobile'):
                    if not self.customer_mobile_validation(mobile_no=kw.get('mobile'),customer_id=partner_id.id):
                        _logger.info("Mobile No Already Exist==============================================>")
                        return {'Staus': 501,'Reason':'Mobile No Already Exist.'}
                    update_list.append(kw.get('mobile'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).mobile = kw.get('mobile')

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

                if kw.get('email'):
                    update_list.append(kw.get('email'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).email = kw.get('email')

                
                if kw.get('country_id'):
                    country_id = self.get_country_id(kw.get('country_id'))
                    if country_id:
                        update_list.append(country_id)
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
        if kw.get('name') and kw.get('detailed_type') and kw.get('invoice_policy') and kw.get('categ_id') and kw.get('default_code') and kw.get('purchase_method') and kw.get('uom_id') and kw.get('uom_po_id'):
            if not self.product_internal_ref_validation(default_code=kw.get('default_code')):
                _logger.info("Internal Ref Already Exist==============================================>")
                return {'Staus': 601,'Reason':'Internal Ref Already Exist.'}

            if kw.get('detailed_type') not in ('consu','service','product'):
                _logger.info("Detailed Type Not Exist, It Must be consu or service or product==============================================>")
                return {'Staus': 602,'Reason':'Detailed Type Not Exist, It Must be consu or service or product.'}

            if kw.get('invoice_policy') not in ('order','delivery'):
                _logger.info("Invoice Policy Not Exist, It Must be order or delivery==============================================>")
                return {'Staus': 603,'Reason':'Invoice Policy Not Exist, It Must be order or delivery.'}

            if kw.get('purchase_method') not in ('purchase','receive'):
                _logger.info("Purchase Method Not Exist, It Must be purchase or receive==============================================>")
                return {'Staus': 604,'Reason':'Purchase Method Not Exist, It Must be purchase or receive.'}

            try:
                categ_id = self.get_product_category(kw.get('categ_id'))
                if not categ_id[1]:
                    return {'Staus': 607,'Reason':'Categ not available in odoo, Kinldy find the List of category in odoo','List':categ_id[0]}

                # customer_tax_list = self.get_tax_ids(kw.get('customer_taxes_id'),tax_type='sale')
                # if not customer_tax_list[1]:
                #     return {'Staus': 608,'Reason':'Customer Tax Not available in odoo, Kinldy find the List of Sale Taxes in odoo','List':customer_tax_list[0]}

                # vendor_tax_list = self.get_tax_ids(kw.get('vendor_taxes_id'),tax_type='purchase')
                # if not vendor_tax_list[1]:
                #     return {'Staus': 609,'Reason':'Vendor Tax Not available in odoo, Kinldy find the List of Purchase Taxes in odoo','List':vendor_tax_list[0]}

                uom_id = self.get_uom_id(kw.get('uom_id'))
                if not uom_id[1]:
                    return {'Staus': 610,'Reason':'Uom Not available in odoo, Kinldy find the List of UOM in odoo','List':uom_id[0]}

                uom_po_id = self.get_uom_id(kw.get('uom_po_id'))
                if not uom_po_id[1]:
                    return {'Staus': 611,'Reason':' Purchase Uom Not available in odoo, Kinldy find the List of UOM in odoo','List':uom_po_id[0]}

                create_vals = {
                        'name': kw.get('name'),
                        'detailed_type': kw.get('detailed_type'),
                        'invoice_policy': kw.get('invoice_policy'),
                        'list_price': kw.get('list_price') if kw.get('list_price') else 1, 
                        'standard_price': kw.get('standard_price'),
                        'categ_id':  categ_id[0],
                        'default_code': kw.get('default_code'),
                        'purchase_method': kw.get('purchase_method'),
                        'sale_ok': True,
                        'purchase_ok': True,
                        # 'taxes_id': [(6, 0,customer_tax_list[0])],
                        # 'supplier_taxes_id': [(6, 0,vendor_tax_list[0])],
                        'uom_id':uom_id[0],
                        'uom_po_id':uom_po_id[0],
                        'create_api_values': kw
                        }
                        
                product_template_id = request.env["product.template"].with_user(2).with_context(
                        {
                           'lang': 'en_US', 
                            'uid': 2, 
                            'allowed_company_ids': [1], 
                        }).create(create_vals)
                if product_template_id:
                    _logger.info("Product Created==============================================> " + str(product_template_id))
                    return {'Staus': 200,'record_id':product_template_id.id}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("name or detailed_type or invoice_policy or list_price or standard_price or categ_id or default_code or purchase_method  or uom id or uom_po_id Is Missing==============================================>")
            return{'Staus': 600,'Reason':'name or detailed_type or invoice_policy or categ_id or default_code or purchase_method Is Missing or uom id or uom_po_id Is Missing' }


    @http.route('/update_product_template', type='json', auth='none', website=True)
    def update_product_template(self, **kw):
        _logger.info("==============================================>Entering Product Updation===============>" + str(kw))
        if kw.get('product_id'):
            product_id = self.get_product_template_id(product=kw.get('product_id'))
            if not product_id:
                _logger.info("ID Does not Exist in odoo==============================================>")
                return {'Staus': 505,'Reason':'ID Doesnot Exist in Odoo, The product May Be archieved or deleted'}

            _logger.info("Product ID To Update==============================================> " + str(product_id))
            update_list =[]
            try:
                # if kw.get('customer_taxes_id'):
                #     customer_tax_list = self.get_tax_ids(kw.get('customer_taxes_id'),tax_type='sale')
                #     if not customer_tax_list[1]: 
                #         return {'Staus': 608,'Reason':'Customer Tax Not available in odoo, Kinldy find the List of Sale Taxes in odoo','List':customer_tax_list[0]}

                # if kw.get('vendor_taxes_id'):
                #     vendor_tax_list = self.get_tax_ids(kw.get('vendor_taxes_id'),tax_type='purchase')
                #     if not vendor_tax_list[1]:
                #         return {'Staus': 609,'Reason':'Vendor Tax Not available in odoo, Kinldy find the List of Purchase Taxes in odoo','List':vendor_tax_list[0]}

                if kw.get('uom_id'):
                    uom_id = self.get_uom_id(kw.get('uom_id'))
                    if not uom_id[1]:
                        return {'Staus': 610,'Reason':'Uom Not available in odoo, Kinldy find the List of UOM in odoo','List':uom_id[0]}

                if kw.get('uom_po_id'):
                    uom_po_id = self.get_uom_id(kw.get('uom_po_id'))
                    if not uom_po_id[1]:
                        return {'Staus': 611,'Reason':' Purchase Uom Not available in odoo, Kinldy find the List of UOM in odoo','List':uom_po_id[0]}

                if kw.get('name'):
                    update_list.append(kw.get('name'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).name = kw.get('name')
                if kw.get('list_price'):
                    update_list.append(kw.get('list_price'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).list_price = kw.get('list_price')
                # if kw.get('standard_price'):
                #     update_list.append(kw.get('standard_price'))
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).standard_price = kw.get('standard_price')
                if kw.get('uom_id'):
                    update_list.append(kw.get('uom_id'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).uom_id = uom_id[0]
                if kw.get('uom_po_id'):
                    update_list.append(kw.get('uom_po_id'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).uom_po_id = uom_po_id[0]
                # if kw.get('customer_taxes_id'):
                #     update_list.append(kw.get('customer_taxes_id'))
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).taxes_id = [(6, 0,[])]
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).taxes_id = [(6, 0,customer_tax_list[0])]
                # if kw.get('vendor_taxes_id'):
                #     update_list.append(kw.get('vendor_taxes_id'))
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).supplier_taxes_id = [(6, 0,[])]
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).supplier_taxes_id = [(6, 0,vendor_tax_list[0])]

                if kw.get('sale_ok'):
                    if str(kw.get('sale_ok')) not in ['1','0']:
                        return {'Staus': 612,'Reason':'Sale Ok Must Be 1 or 0'}
                    update_list.append(kw.get('sale_ok'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).sale_ok = True if kw.get('sale_ok') == "1" else False

                if kw.get('purchase_ok'):
                    if str(kw.get('purchase_ok')) not in ['1','0']:
                        return {'Staus': 612,'Reason':'Purchase Ok Must Be 1 or 0'}
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).purchase_ok = True if kw.get('purchase_ok') == "1" else False
                    update_list.append(kw.get('purchase_ok'))

                product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).write_api_values = kw

                if update_list:
                    return {'Staus': 200,'Status':'Successfully Updated'+'-'+str(update_list)}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}

        else:
            _logger.info("Product Id Is Missing==============================================>")
            return {'Staus': 500,'Reason':'Product Id Is Missing'}




    @http.route('/create_sale_order', type='json', auth='none', website=True)
    def create_sale_order(self, **kw):
        _logger.info("Mocdoc Json write_api_valuesues==============================================>"+str(kw))
        if kw.get('customer_id') and kw.get('product_list') and kw.get('currency_type'):
            try:
                if self.check_price_validation(product_list=kw.get('product_list')):
                    _logger.info("Mocdoc Price Is lesser than 0.1 ==============================================>")
                    return {'Staus': 704,'Reason':'Moc Doc Unit Price Is Lesser Than 0.1'}

                for i in kw.get('product_list'):
                    if i.get('customer_tax'):
                        customer_tax_list = self.get_tax_ids(i.get('customer_tax'),tax_type='sale')
                        if not customer_tax_list[1]: 
                            return {'Staus': 608,'Reason':'Customer Tax Not available in odoo, Kinldy find the List of Sale Taxes in odoo','List':customer_tax_list[0]}

                partner_id = self.search_customer_id_validation(kw.get('customer_id'))
                product_id = self.product_id_validation(product_list=kw.get('product_list'))

                if kw.get('insurance_provider_id'):
                    insurance_provider = self.search_insurance_provider_id_validation(kw.get('insurance_provider_id'))
                    if not insurance_provider[1]:
                        _logger.info("Insurance Provider Does not Exist in odoo==============================================>")
                        return {'Staus': 707,'Reason':'Insurance Provider Does not Exist in Odoo, Kinldy find the List of Insurance Providers in odoo','List':insurance_provider[0]}

                if not partner_id:
                    _logger.info("Partner ID Does not Exist in odoo==============================================>")
                    return {'Staus': 705,'Reason':'Partner ID Doesnot Exist in Odoo, The Patient May Be archieved or deleted'}
                if product_id[1]:
                    _logger.info("Product ID Does not Exist in odoo==============================================>" + str(product_id))
                    return {'Staus': 706,'Reason':'Product ID Doesnot Exist in Odoo, The product May Be archieved or deleted' + str(product_id)}
                    


                # if kw.get('journal_type'):

                api_priclist = False
                if kw.get('currency_type'):
                    api_priclist = self.search_pricleist()

                sale_order_id = request.env["sale.order"].with_user(2).create(
                        {
                            'partner_id': partner_id.id,
                            'moc_doc_ref':kw.get('moc_doc_ref') if kw.get('moc_doc_ref') else False,
                            'create_api_values':kw,
                            'make_so_readonly':True,
                            'insurance_provider_id': insurance_provider[0].id if kw.get('insurance_provider_id') else '',
                            'agreed_amount': kw.get('agreed_amount') if kw.get('agreed_amount') else 0.0,
                            'actual_paid': kw.get('actual_paid') if kw.get('actual_paid') else 0.0,
                            'pricelist_id':api_priclist.id
                        })

                if sale_order_id:
                    _logger.info("Sale Order Created==============================================> " + str(sale_order_id))
                    for i in product_id[0]:
                        sale_order_line_id = request.env["sale.order.line"].with_user(2).create(
                            {
                                'product_id': i.get('product_id'),
                                'order_id':sale_order_id.id,
                                'product_uom_qty':i.get('qty'),
                                'price_unit':i.get('moc_doc_price_unit'),
                                'tax_id': i.get('tax_id'),
                                'discount': i.get('disc')
                            })
                        
                        _logger.info("Sale Order Line Created==============================================> " + str(sale_order_line_id))

                    sale_order_id.sudo().action_confirm()


                    picking_id = request.env["stock.picking"].with_user(2).search([('origin','=',sale_order_id.name)])
                    if picking_id and picking_id.products_availability == 'Available':
                        picking_id.action_set_quantities_to_reservation()
                        picking_id.button_validate()

                    return {'Staus': 200,'record_id':sale_order_id.name}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("partner_id or pricelist or product_list Is Missing==============================================>")
            return{'Staus': 700,'Reason':'customer_id or product_list Is Missing'}



    @http.route('/create_purchase_order', type='json', auth='none', website=True)
    def create_purchase_order(self, **kw):
        if kw.get('customer_id') and kw.get('product_list'):
            try:
                if self.check_price_validation(product_list=kw.get('product_list')):
                    _logger.info("Mocdoc Price Is lesser than 0.1 ==============================================>")
                    return {'Staus': 804,'Reason':'Moc Doc Unit Price Is Lesser Than 0.1'}

                for i in kw.get('product_list'):
                    if i.get('vendor_tax'):
                        vendor_tax_list = self.get_tax_ids(i.get('vendor_tax'),tax_type='purchase')
                        if not vendor_tax_list[1]: 
                            return {'Staus': 808,'Reason':'Vendor Tax Not available in odoo, Kinldy find the List of Sale Taxes in odoo','List':vendor_tax_list[0]}


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
                            'moc_doc_ref':kw.get('moc_doc_ref') if kw.get('moc_doc_ref') else False,
                            'create_api_values':kw,
                            'make_po_readonly':True
                        })
                if purchase_order_id:
                    _logger.info("Purchase Order Created==============================================> " + str(purchase_order_id))
                    for i in product_id[0]:
                        purchase_order_line_id = request.env["purchase.order.line"].with_user(2).create(
                            {
                                'product_id': i.get('product_id'),
                                'order_id':purchase_order_id.id,
                                'product_qty':i.get('qty'),
                                'price_unit':i.get('moc_doc_price_unit'),
                                'taxes_id': i.get('tax_id') 
                            })
                        _logger.info("Purchase Order Line Created==============================================> " + str(purchase_order_line_id))

                    purchase_order_id.sudo().button_confirm()

                    # picking_id = request.env["stock.picking"].with_user(2).search([('origin','=',purchase_order_id.name)])
                    # picking_id.action_set_quantities_to_reservation()
                    # picking_id.button_validate()

                    return {'Staus': 200,'record_id':purchase_order_id.name}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("partner_id or product_list Is Missing==============================================>")
            return{'Staus': 800,'Reason':'customer_id or product_list Is Missing'}


    @http.route('/create_payment', type='json', auth='none', website=True)
    def create_payment(self, **kw):
        _logger.info("MoCDOC JSON==============================================>"+ str(kw))
        if kw.get('customer_id') and kw.get('amount') and kw.get('currency_id') and kw.get('journal_type'):
            try:
                partner_id = self.search_customer_id_validation(customer_id=kw.get('customer_id'))
                currency_id = self.search_currency_id_validation(currency_id=kw.get('currency_id'))

                if not partner_id:
                    _logger.info("Partner ID Does not Exist in odoo==============================================>")
                    return {'Staus': 305,'Reason':'Patient ID Doesnot Exist in Odoo, The Patient May Be archieved or deleted'}

                if not currency_id:
                    _logger.info("Currency ID Does not Exist in odoo==============================================>")
                    return {'Staus': 306,'Reason':'Currency ID Doesnot Exist in Odoo, The Currency Be archieved or deleted'}

                if kw.get('amount') < 1.0:
                    _logger.info("Amount Is lesser than 1.0 ==============================================>")
                    return {'Staus': 304,'Reason':'Price Is Lesser Than 0.1'}

                if kw.get('journal_type') not in ['Bank','Cash']:
                    _logger.info("Journal Type Is Not in Bank or Cash ==============================================>")
                    return {'Staus': 305,'Reason':'journal Type Is Not in Bank or Cash'}

                journal_id = request.env["account.journal"].sudo().search([('name','=',kw.get('journal_type'))],limit =1)
                if not journal_id:
                    _logger.info("Journal Not found in odoo ==============================================>")
                    return {'Staus': 306,'Reason':'Journal Not found in odoo '}

                payment_id = request.env["account.payment"].with_user(2).create(
                        {
                            'partner_id': partner_id.id,
                            'payment_type': 'inbound',
                            'amount': kw.get('amount'),
                            'currency_id': currency_id.id,
                            'journal_id': journal_id.id,
                            'ref': kw.get('ref'),
                        })
                
                if payment_id:
                    _logger.info("Payment Created==============================================> " + str(payment_id))
                    payment_id.action_post()

                    return {'Staus': 200,'record_id':payment_id.name}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                return {'Staus': 503,'Reason':str(e)}
        else:
            _logger.info("partner_id or amount or currency Is Missing==============================================>")
            return{'Staus': 300,'Reason':'customer_id or amount or currency or journal Type Is Missing'}


