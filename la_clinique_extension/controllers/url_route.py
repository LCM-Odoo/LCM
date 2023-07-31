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

    def search_cash_customer_validation(self):
        partner_id = request.env["res.partner"].sudo().search([('active','=',True),('is_cash_customer','=',True)],limit=1)
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


    def search_location(self,location=False):
        stock_location_id = request.env["stock.location"].sudo().search([('name','=',location)],limit=1)
        if stock_location_id:
            return stock_location_id
        else:
            stock_location_id = request.env["stock.location"].sudo().search([('is_missing_loc','=',True)],limit=1)
            if stock_location_id:
                return stock_location_id
        return False

    def search_internal_transfer_loc(self,location=False):
        stock_location_id = request.env["stock.location"].sudo().search([('name','=',location)],limit=1)
        if stock_location_id:
            return stock_location_id,True
        else:
            stock_location_id = [i.name for i in request.env["stock.location"].sudo().search([])]
            return stock_location_id,False




    def product_id_validation(self,product_list=False,internal_transfer=False):
        Product_missing_list =[]
        Product_available_list =[]
        
        for i in product_list:
            location_id = False
            tax_list = []
            if i.get('product_id'):
                product_template_id = request.env["product.template"].sudo().search([('active','=',True),('id','=',i.get('product_id'))])
                if not product_template_id:Product_missing_list.append(i.get('product_id'))
                if product_template_id:
                    product_id = request.env["product.product"].sudo().search([('active','=',True),('product_tmpl_id','=',product_template_id.id)])

                    if internal_transfer:
                        Product_available_list.append(
                            {
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'qty_done': i.get('product_qty'),
                                'product_uom': product_id.uom_id.id,
                            })
                    else:
                        if i.get('customer_tax'):
                            tax_list = self.get_tax_ids(i.get('customer_tax'),tax_type='sale')

                        if i.get('vendor_tax'):
                            tax_list = self.get_tax_ids(i.get('vendor_tax'),tax_type='purchase')

                        if i.get('moc_doc_location'):
                            location_id = self.search_location(location=i.get('moc_doc_location'))

                        Product_available_list.append(
                            {
                                'product_id': product_id.id,
                                'qty': i.get('product_qty'),
                                'moc_doc_price_unit': i.get('moc_doc_price_unit'),
                                'tax_id': [(6, 0,tax_list[0])] if tax_list else [(6, 0,tax_list)],
                                'disc': i.get('disc') if i.get('disc') else 0.0,
                                'moc_doc_location_id':location_id.id if location_id else False
                            })
            else:
                Product_missing_list.append('Product Id not sent from Mocdoc')

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

    def search_pricleist(self,currency_name=False):
        pricelist_id = request.env["product.pricelist"].sudo().search([('is_moc_doc_priclist','=',True),('currency_id.name','=',currency_name)],limit=1)
        if pricelist_id:
            return pricelist_id
        else:
            False

    def search_journal(self,journal_type=False,from_sale=False):
        journal_id = request.env["account.journal"].sudo().search([('name','=',journal_type)],limit =1)
        if journal_id:
            if from_sale:
                return journal_id.id
            else:
                return journal_id,False
        else:
            if from_sale:
                return False
            else:
                journal_list = [i.name for i in request.env["account.journal"].sudo().search([('type','in',('bank','cash'))])]
                return journal_list,True
       


    def search_internal_transfer_operation_type(self):
        internal_picking_id = request.env["stock.picking.type"].sudo().search([('is_api_transfer','=',True)],limit=1)
        if internal_picking_id:
            return internal_picking_id
        else:
            return False

    def create_error_logs(self,mocdoc_api_values='',api_type='',model='',response=''):
        try:
            if mocdoc_api_values and api_type and model and response:

                ref = mocdoc_api_values.get('moc_doc_ref')
                body = ''
                if mocdoc_api_values.get('product_list'):
                    for i in mocdoc_api_values.get('product_list'):
                          body += (str(i) + "<br>")

                api_log_id = request.env["api.logs"].with_user(2).with_context(
                            {
                               'lang': 'en_US', 
                                'uid': 2, 
                                'allowed_company_ids': [1], 
                            }).create({
                                        'name':response,
                                        'mocdoc_api_values':mocdoc_api_values,
                                        'api_type':api_type,
                                        'model':model,
                                        'moc_doc_ref':ref if ref else False,
                                        'product_list':body if body else '',
                            })
                if api_log_id:
                    _logger.info("Error Log Created==============================================>" + str(api_log_id))

                    # Mail Content
                    try:
                        api_log_id.send_mail_to_clinet(mocdoc_api_values='',api_type='',model='',response='')
                    except Exception as e:
                        _logger.error("Mail is Not delivered==============================================> " + str(e))

        except Exception as e:
                    _logger.error("Error Log not created in Odoo==============================================> " + str(e))


      
    @http.route('/create_customer', type='json', auth='none', website=True)
    def create_customer(self, **kw):
        _logger.info("==============================================>Entering Customer Creation=========================================================>")
        if kw.get('name') and kw.get('moc_doc_id') and kw.get('type'):
            if kw.get('type') not in ('cus','ven'):
                _logger.info("Type Not In Cus Or Ven==============================================>" + str(kw.get('type')))
                response = {'Status': 506,'Reason':'Patient Type Not In Cus Or Ven.'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='customer',response=str(response))
                return response

            # if not self.customer_mobile_validation(mobile_no=kw.get('mobile')):
            #     _logger.info("Mobile No Already Exist==============================================>")
            #     return {'Status': 501,'Reason':'Mobile No Already Exist.'}

            if not self.customer_moc_doc_id_validation(moc_doc_id=kw.get('moc_doc_id')):
                _logger.info("Moc Doc Id  Already Exist==============================================>")
                response = {'Status': 504,'Reason':'Moc Doc Id  Already Exist for Another Patient In Odoo. Kindly provide a Unique One'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='customer',response=str(response))
                return response

            name = str(kw.get('name')).strip()
            if kw.get('last_name'):
                name = name + ' '+ str(kw.get('last_name')).strip()
                
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
                                'name': name, 
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
                    return {'Status': 200,'record_id':partner_id.id}
                else:
                     _logger.error("Customer Not Created==============================================>")
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='customer',response=str(response))
                return response
        else:
            _logger.info("Name or Moc Doc Id Is Missing==============================================>")
            response = {'Status': 500,'Reason':'Name or Moc Doc Id or Patient Type(Customer Or Vendor In Odoo) Is Missing'}
            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='customer',response=str(response))
            return response


    @http.route('/customer_update', type='json', auth='none', website=True)
    def customer_update(self, **kw):
        _logger.info("==============================================>Entering Customer Updation===============>" + str(kw))
        if kw.get('customer_id'):
            partner_id = self.search_customer_id_validation(customer_id=kw.get('customer_id'))
            if not partner_id:
                _logger.info("ID Does not Exist in odoo==============================================>")
                response = {'Status': 505,'Reason':'ID Does not Exist in Odoo, The Patient May Be archived or deleted'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='customer',response=str(response))
                return response

            _logger.info("Partner ID To Update==============================================> " + str(partner_id))
            update_list =[]
            try:
                if kw.get('mobile'):
                    # if not self.customer_mobile_validation(mobile_no=kw.get('mobile'),customer_id=partner_id.id):
                    #     _logger.info("Mobile No Already Exist==============================================>")
                    #     return {'Status': 501,'Reason':'Mobile No Already Exist.'}
                    update_list.append(kw.get('mobile'))
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).mobile = kw.get('mobile')

                if kw.get('name'):
                    name = str(kw.get('name')).strip() 
                    if kw.get('last_name'):
                        name = name + ' '+ str(kw.get('last_name')).strip()

                    update_list.append(name)
                    partner_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).name = name

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
                    return {'Status': 200,'Reason':'Successfully Updated'+'-'+str(update_list)}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='customer',response=str(response))
                return response
        else:
            _logger.info("Customer Id Is Missing==============================================>")
            response = {'Status': 500,'Reason':'Customer Id Is Missing'}
            self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='customer',response=str(response))
            return response


    @http.route('/create_product_template', type='json', auth='none', website=True)
    def create_product_template(self, **kw):
        _logger.info("==============================================>Entering Product Creation===============>" + str(kw))
        if kw.get('name') and kw.get('detailed_type') and kw.get('invoice_policy') and kw.get('categ_id') and kw.get('default_code') and kw.get('purchase_method'):
            if not self.product_internal_ref_validation(default_code=kw.get('default_code')):
                _logger.info("Internal Ref Already Exist==============================================>")
                response = {'Status': 601,'Reason':'Internal Ref Already Exist.'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                return response

            if kw.get('detailed_type') not in ('consu','service','product'):
                _logger.info("Detailed Type Not Exist, It Must be consu or service or product==============================================>")
                response = {'Status': 602,'Reason':'Detailed Type Not Exist, It Must be consu or service or product.'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                return response

            if kw.get('invoice_policy') not in ('order','delivery'):
                _logger.info("Invoice Policy Not Exist, It Must be order or delivery==============================================>")
                response = {'Status': 603,'Reason':'Invoice Policy Not Exist, It Must be order or delivery.'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                return response

            if kw.get('purchase_method') not in ('purchase','receive'):
                _logger.info("Purchase Method Not Exist, It Must be purchase or receive==============================================>")
                response = {'Status': 604,'Reason':'Purchase Method Not Exist, It Must be purchase or receive.'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                return response

            try:
                categ_id = self.get_product_category(kw.get('categ_id'))
                if not categ_id[1]:
                    response = {'Status': 607,'Reason':'Categ not available in odoo, Kindly find the List of category in odoo','List':categ_id[0]}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                    return response


                # customer_tax_list = self.get_tax_ids(kw.get('customer_taxes_id'),tax_type='sale')
                # if not customer_tax_list[1]:
                #     return {'Status': 608,'Reason':'Customer Tax Not available in odoo, Kinldy find the List of Sale Taxes in odoo','List':customer_tax_list[0]}

                # vendor_tax_list = self.get_tax_ids(kw.get('vendor_taxes_id'),tax_type='purchase')
                # if not vendor_tax_list[1]:
                #     return {'Status': 609,'Reason':'Vendor Tax Not available in odoo, Kinldy find the List of Purchase Taxes in odoo','List':vendor_tax_list[0]}

                # uom_id = self.get_uom_id(kw.get('uom_id'))
                # if not uom_id[1]:
                #     response = {'Status': 610,'Reason':'Uom Not available in odoo, Kindly find the List of UOM in odoo','List':uom_id[0]}
                #     self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                #     return response

                # uom_po_id = self.get_uom_id(kw.get('uom_po_id'))
                # if not uom_po_id[1]:
                #     response = {'Status': 611,'Reason':' Purchase Uom Not available in odoo, Kindly find the List of UOM in odoo','List':uom_po_id[0]}
                #     self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                #     return response

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
                        # 'uom_id':uom_id[0],
                        # 'uom_po_id':uom_po_id[0],
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
                    return {'Status': 200,'record_id':product_template_id.id}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
                return response
        else:
            _logger.info("name or detailed_type or invoice_policy or categ_id or default_code or purchase_method  Is Missing==============================================>")
            response = {'Status': 600,'Reason':'name or detailed_type or invoice_policy or categ_id or default_code or purchase_method Is Missing  Is Missing' }
            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='product',response=str(response))
            return response


    @http.route('/update_product_template', type='json', auth='none', website=True)
    def update_product_template(self, **kw):
        _logger.info("==============================================>Entering Product Updation===============>" + str(kw))
        if kw.get('product_id'):
            product_id = self.get_product_template_id(product=kw.get('product_id'))
            if not product_id:
                _logger.info("ID Does not Exist in odoo==============================================>")
                response = {'Status': 505,'Reason':'ID Does not Exist in Odoo, The product May Be archived or deleted in Odoo'}
                self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='product',response=str(response))
                return response

            _logger.info("Product ID To Update==============================================> " + str(product_id))
            update_list =[]
            try:
                # if kw.get('customer_taxes_id'):
                #     customer_tax_list = self.get_tax_ids(kw.get('customer_taxes_id'),tax_type='sale')
                #     if not customer_tax_list[1]: 
                #         return {'Status': 608,'Reason':'Customer Tax Not available in odoo, Kinldy find the List of Sale Taxes in odoo','List':customer_tax_list[0]}

                # if kw.get('vendor_taxes_id'):
                #     vendor_tax_list = self.get_tax_ids(kw.get('vendor_taxes_id'),tax_type='purchase')
                #     if not vendor_tax_list[1]:
                #         return {'Status': 609,'Reason':'Vendor Tax Not available in odoo, Kinldy find the List of Purchase Taxes in odoo','List':vendor_tax_list[0]}

                # if kw.get('uom_id'):
                #     uom_id = self.get_uom_id(kw.get('uom_id'))
                #     if not uom_id[1]:
                #         response = {'Status': 610,'Reason':'Uom Not available in odoo, Kindly find the List of UOM in odoo','List':uom_id[0]}
                #         self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='product',response=str(response))
                #         return response

                # if kw.get('uom_po_id'):
                #     uom_po_id = self.get_uom_id(kw.get('uom_po_id'))
                #     if not uom_po_id[1]:
                #         response = {'Status': 611,'Reason':' Purchase Uom Not available in odoo, Kindly find the List of UOM in odoo','List':uom_po_id[0]}
                #         self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='product',response=str(response))
                #         return response

                if kw.get('name'):
                    update_list.append(kw.get('name'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).name = kw.get('name')
                if kw.get('list_price'):
                    update_list.append(kw.get('list_price'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).list_price = kw.get('list_price')
                # if kw.get('standard_price'):
                #     update_list.append(kw.get('standard_price'))
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).standard_price = kw.get('standard_price')
                # if kw.get('uom_id'):
                #     update_list.append(kw.get('uom_id'))
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).uom_id = uom_id[0]
                # if kw.get('uom_po_id'):
                #     update_list.append(kw.get('uom_po_id'))
                #     product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).uom_po_id = uom_po_id[0]
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
                        return {'Status': 612,'Reason':'Sale Ok Must Be 1 or 0'}
                    update_list.append(kw.get('sale_ok'))
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).sale_ok = True if kw.get('sale_ok') == "1" else False

                if kw.get('purchase_ok'):
                    if str(kw.get('purchase_ok')) not in ['1','0']:
                        return {'Status': 612,'Reason':'Purchase Ok Must Be 1 or 0'}
                    product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).purchase_ok = True if kw.get('purchase_ok') == "1" else False
                    update_list.append(kw.get('purchase_ok'))

                product_id.sudo().with_context({'lang': 'en_US','allowed_company_ids': [1]}).write_api_values = kw

                if update_list:
                    return {'Status': 200,'Reason':'Successfully Updated'+'-'+str(update_list)}
            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='product',response=str(response))
                return response

        else:
            _logger.info("Product Id Is Missing==============================================>")
            response = {'Status': 500,'Reason':'Product Id Is Missing'}
            self.create_error_logs(mocdoc_api_values=kw,api_type='update',model='product',response=str(response))
            return response



    def search_sale_validation(self,moc_doc_ref=False):
        if moc_doc_ref:
            sale_order_list = [i.name for i in request.env["sale.order"].sudo().search([('moc_doc_ref','=',moc_doc_ref),('state','!=','cancel')])]
            if sale_order_list:
                return sale_order_list
            else:
                return False



    @http.route('/create_sale_order', type='json', auth='none', website=True)
    def create_sale_order(self, **kw):
        _logger.info("Mocdoc Json write_api_valuesues==============================================>"+str(kw))
        if kw.get('product_list') and kw.get('currency_type'):
            try:
                if not kw.get('bill_type'):
                    response = {'Status': 714,'Reason':'Bill Type Is Not Sent from Mocdoc'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                    return response

                if kw.get('bill_type') and kw.get('bill_type') not in ['pharmacy','i/p','o/p']:
                    response = {'Status': 715,'Reason':'Bill Type Is Not in i/p, o/p, pharmacy'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                    return response


                if kw.get('bill_type') == 'i/p':
                    sale_list = self.search_sale_validation(kw.get('moc_doc_ref'))
                    if sale_list:
                        mail_id = request.env['sale.order'].send_mail_client(sale_list=sale_list,moc_doc_ref=kw.get('moc_doc_ref'))
                        if mail_id:
                            return {'Status': 200,'Mail_Sent':True}
                        else:
                            response = {'Status': 716,'Reason':'Bill Update Mail Not Sent to Clinet, Kinldy Contact Odoo Support'}
                            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                            return response


                patient_type = ''
                if kw.get('patient_type') and kw.get('patient_type') in ('in','out','self'):
                    patient_type = kw.get('patient_type')

                if not patient_type:
                    response = {'Status': 711,'Reason':'Patinet Type Is not in (in/out/self) for the Bill'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                    return response

                if patient_type != 'self' and not kw.get('customer_id'):
                    response = {'Status': 712,'Reason':'Customer Id not sent from Mocdoc for the Bill'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                    return response


                if self.check_price_validation(product_list=kw.get('product_list')):
                    _logger.info("Mocdoc Price Is lesser than 0.1 ==============================================>")
                    response = {'Status': 704,'Reason':'Moc Doc Unit Price Is Lesser Than 0.1'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                    return response

                tax_note = False
                for i in kw.get('product_list'):
                    if i.get('customer_tax'):
                        customer_tax_list = self.get_tax_ids(i.get('customer_tax'),tax_type='sale')
                        if not customer_tax_list[1]: 
                            response = {'Status': 608,'Reason':'Customer Tax Not available in odoo, Kindly find the List of Sale Taxes in odoo','List':customer_tax_list[0]}
                            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                            # return response
                    else:
                        response = {'Status': 608,'Reason':'Customer Tax is not sent from Mocdoc Please find the Values','List':str(kw)}
                        self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                        # return response

                if patient_type == 'self':
                    partner_id = self.search_cash_customer_validation()
                    if not partner_id:
                        _logger.info("Cash Customer Is Not Configured in odoo==============================================>")
                        response = {'Status': 713,'Reason':'Cash Customer Is not Configured in Odoo'}
                        self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                        return response
                else:
                    partner_id = self.search_customer_id_validation(customer_id=kw.get('customer_id'))
                    if not partner_id:
                        _logger.info("Partner ID Does not Exist in odoo==============================================>")
                        response = {'Status': 705,'Reason':'Partner ID Does not Exist in Odoo, The Patient May Be archived or deleted'}
                        self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                        return response

                product_id = self.product_id_validation(product_list=kw.get('product_list'))
                currency_id = self.search_currency_id_validation(currency_id=kw.get('currency_type'))

                if kw.get('insurance_provider_id'):
                    insurance_provider = self.search_insurance_provider_id_validation(kw.get('insurance_provider_id'))
                    if not insurance_provider[1]:
                        _logger.info("Insurance Provider Does not Exist in odoo==============================================>")
                        response = {'Status': 707,'Reason':'Insurance Provider Does not Exist in Odoo, Kindly find the List of Insurance Providers in odoo','List':insurance_provider[0]}
                        self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                        return response
                
                if product_id[1]:
                    _logger.info("Product ID Does not Exist in odoo==============================================>" + str(product_id))
                    response = {'Status': 706,'Reason':'Product ID Does not Exist in Odoo, The product May Be archived or deleted' + str(product_id)}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                    return response

                if not currency_id:
                    _logger.info("Currency ID Does not Exist in odoo==============================================>")
                    response = {'Status': 709,'Reason':'Currency ID Does not Exist in Odoo, The Currency Be archived or deleted'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                    return response
                    
                api_pricelist = False
                if kw.get('currency_type'):
                    api_pricelist = self.search_pricleist(currency_name=kw.get('currency_type'))


                amount = 0.0
                journal_id = False

                if kw.get('amount') > 0.0:
                    amount = kw.get('amount')
                    if not kw.get('journal_type'):
                        response = {'Status': 710,'Reason':'Journal Not Sent From Mocdoc'}
                        self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                        return response

                    journal_id = self.search_journal(journal_type=kw.get('journal_type'),from_sale=True)
                    if not journal_id:
                        _logger.info("Journal Not found in odoo ==============================================>")
                        response = {'Status': 708,'Reason':'Journal Not found in odoo'}
                        self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                        return response


                sale_order_id = request.env["sale.order"].with_user(2).create(
                        {
                            'partner_id': partner_id.id,
                            'moc_doc_ref':kw.get('moc_doc_ref') if kw.get('moc_doc_ref') else False,
                            'create_api_values':kw,
                            'make_so_readonly':True,
                            'insurance_provider_id': insurance_provider[0].id if kw.get('insurance_provider_id') else '',
                            'agreed_amount': kw.get('agreed_amount') if kw.get('agreed_amount') else 0.0,
                            'actual_paid': kw.get('actual_paid') if kw.get('actual_paid') else 0.0,
                            'pricelist_id':api_pricelist.id,
                            'patient_type' : patient_type,
                            'sale_bill_amount': amount,
                            'sale_bill_type':journal_id,
                            'sale_bill_currency': currency_id.id
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
                                'discount': i.get('disc'),
                                'moc_doc_location_id': i.get('moc_doc_location_id'),
                            })
                        
                        _logger.info("Sale Order Line Created==============================================> " + str(sale_order_line_id))

                    sale_order_id.sudo().action_confirm()
                    sale_order_id.create_payment()

                    picking_id = request.env["stock.picking"].with_user(2).search([('origin','=',sale_order_id.name)])
                    if picking_id:
                        picking_id.do_unreserve()
                        picking_id.action_assign()
                    # if picking_id and picking_id.products_availability == 'Available':
                        # picking_id.action_set_quantities_to_reservation()
                        # picking_id.button_validate()

                    return {'Status': 200,'record_id':sale_order_id.name}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
                return response
        else:
            _logger.info("currency_type or product_list Is Missing==============================================>")
            response = {'Status': 700,'Reason':'currency_type or product_list Is Missing'}
            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='sale',response=str(response))
            return response



    @http.route('/create_purchase_order', type='json', auth='none', website=True)
    def create_purchase_order(self, **kw):
        _logger.info("Mocdoc Json create_api_valuesues==============================================>"+str(kw))
        if kw.get('customer_id') and kw.get('product_list') and kw.get('currency_type'):
            try:
                if self.check_price_validation(product_list=kw.get('product_list')):
                    _logger.info("Mocdoc Price Is lesser than 0.1 ==============================================>")
                    response = {'Status': 804,'Reason':'Moc Doc Unit Price Is Lesser Than 0.1'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
                    return response

                for i in kw.get('product_list'):
                    if i.get('vendor_tax'):
                        vendor_tax_list = self.get_tax_ids(i.get('vendor_tax'),tax_type='purchase')
                        if not vendor_tax_list[1]: 
                            response = {'Status': 808,'Reason':'Vendor Tax Not available in odoo, Kinldy find the List of Sale Taxes in odoo','List':vendor_tax_list[0]}
                            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
                            return response
                    else:
                        response = {'Status': 808,'Reason':'Vendor Tax Not send from Mocdoc, Please find the Value','List':str(kw)}
                        self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
                        return response



                partner_id = self.search_customer_id_validation(customer_id=kw.get('customer_id'))
                product_id = self.product_id_validation(product_list=kw.get('product_list'))
                currency_id = self.search_currency_id_validation(currency_id=kw.get('currency_type'))


                if not partner_id:
                    _logger.info("Partner ID Does not Exist in odoo==============================================>")
                    response = {'Status': 805,'Reason':'Partner ID Does not Exist in Odoo, The Patient May Be archived or deleted'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
                    return response

                if product_id[1]:
                    _logger.info("Product ID Does not Exist in odoo==============================================>" + str(product_id))
                    response = {'Status': 806,'Reason':'Product ID Does not Exist in Odoo, The product May Be archived or deleted' + str(product_id)}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
                    return response

                if not currency_id:
                    _logger.info("Currency ID Does not Exist in odoo==============================================>")
                    response = {'Status': 807,'Reason':'Currency ID Does not Exist in Odoo, The Currency Be archived or deleted'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
                    return response


                purchase_order_id = request.env["purchase.order"].with_user(2).create(
                        {
                            'partner_id': partner_id.id,
                            'currency_id': currency_id.id,
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

                    return {'Status': 200,'record_id':purchase_order_id.name}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
                return response
        else:
            _logger.info("partner_id or currency_type or  product_list Is Missing==============================================>")
            response = {'Status': 800,'Reason':'customer_id or currency_type or product_list Is Missing'}
            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='purchase',response=str(response))
            return response


    @http.route('/create_payment', type='json', auth='none', website=True)
    def create_payment(self, **kw):
        _logger.info("MoCDOC JSON==============================================>"+ str(kw))
        if kw.get('customer_id') and kw.get('amount') and kw.get('currency_id') and kw.get('journal_type'):
            try:
                partner_id = self.search_customer_id_validation(customer_id=kw.get('customer_id'))
                currency_id = self.search_currency_id_validation(currency_id=kw.get('currency_id'))

                if not partner_id:
                    _logger.info("Partner ID Does not Exist in odoo==============================================>")
                    response = {'Status': 305,'Reason':'Patient ID Does not Exist in Odoo, The Patient May Be archived or deleted'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='payment',response=str(response))
                    return response

                if not currency_id:
                    _logger.info("Currency ID Does not Exist in odoo==============================================>")
                    response = {'Status': 306,'Reason':'Currency ID Does not Exist in Odoo, The Currency Be archived or deleted'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='payment',response=str(response))
                    return response

                if kw.get('amount') < 1.0:
                    _logger.info("Amount Is lesser than 1.0 ==============================================>")
                    response = {'Status': 304,'Reason':'Price Is Lesser Than 0.1'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='payment',response=str(response))
                    return response

                journal_id = self.search_journal(journal_type=kw.get('journal_type'))
                if journal_id[1]:
                    _logger.info("Journal Not found in odoo ==============================================>")
                    response = {'Status': 305,'Reason':'Journal Not found in odoo, Kinldy find the List of Payment Methods','List':journal_id[0]}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='payment',response=str(response))
                    return response

                payment_id = request.env["account.payment"].with_user(2).create(
                        {
                            'partner_id': partner_id.id,
                            'payment_type': 'inbound',
                            'amount': kw.get('amount'),
                            'currency_id': currency_id.id,
                            'journal_id': journal_id[0].id,
                            'ref': kw.get('ref'),
                        })
                
                if payment_id:
                    _logger.info("Payment Created==============================================> " + str(payment_id))
                    payment_id.action_post()

                    return {'Status': 200,'record_id':payment_id.name}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='payment',response=str(response))
                return response
        else:
            _logger.info("partner_id or amount or currency Is Missing==============================================>")
            response = {'Status': 300,'Reason':'customer_id or amount or currency or journal Type Is Missing'}
            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='payment',response=str(response))
            return response


    @http.route('/create_internal_transfer', type='json', auth='none', website=True)
    def create_internal_transfer(self, **kw):
        _logger.info("MoCDOC JSON==============================================>"+ str(kw))
        if kw.get('from_location') and kw.get('to_location') and kw.get('product_list'):
            try:
                from_location_id = self.search_internal_transfer_loc(location=kw.get('from_location'))
                to_location_id = self.search_internal_transfer_loc(location=kw.get('to_location'))

                product_id = self.product_id_validation(product_list=kw.get('product_list'),internal_transfer=True)

                if not from_location_id[1]:
                    _logger.info("From Location Does not Exist in odoo==============================================>")
                    response = {'Status': 405,'Reason':'From Location Does Not Exist in Odoo, Kinldy find the List of Locations','List':from_location_id[0]}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='internal_transfer',response=str(response))
                    return response

                if not to_location_id[1]:
                    _logger.info("To Location Does not Exist in odoo==============================================>")
                    response = {'Status': 406,'Reason':'To Location Does Not Exist in Odoo, Kinldy find the List of Locations','List':to_location_id[0]}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='internal_transfer',response=str(response))
                    return response

                if product_id[1]:
                    _logger.info("Product ID Does not Exist in odoo==============================================>" + str(product_id))
                    response = {'Status': 406,'Reason':'Product ID Does not Exist in Odoo, The product May Be archived or deleted' + str(product_id)}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='internal_transfer',response=str(response))
                    return response

                internal_transfer_id = self.search_internal_transfer_operation_type()
                if not internal_transfer_id:
                    _logger.info("Is API Internal Transfer Does not Configured in odoo, Kindly do the Configuration==============================================>" + str(product_id))
                    response = {'Status': 407,'Reason':'Is API Internal Transfer Does not Configured in odoo, Kindly do the Configuration'}
                    self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='internal_transfer',response=str(response))
                    return response


                picking_id = request.env["stock.picking"].with_user(2).create(
                        {
                            'location_id': from_location_id[0].id,
                            'location_dest_id': to_location_id[0].id,
                            'picking_type_id': internal_transfer_id.id,
                            'moc_doc_ref': kw.get('moc_doc_ref') if kw.get('moc_doc_ref') else False,
                            'is_int_api':True,
                            'create_api_values':kw,
                        })

                if picking_id:
                    _logger.info("Transfer Created==============================================> " + str(picking_id))
                    for i in product_id[0]:
                        move_id = request.env["stock.move"].with_user(2).create(
                            {
                                'product_id': i.get('product_id'),
                                'product_uom_qty':i.get('qty_done'),
                                'picking_id':picking_id.id,
                                'name': i.get('name'),
                                'description_picking': i.get('name'),
                                'product_uom':i.get('product_uom'),
                                'location_id': from_location_id[0].id,
                                'location_dest_id': to_location_id[0].id,
                            })
                        _logger.info("Move Line Created==============================================> " + str(move_id))

                    if picking_id:
                        picking_id.action_confirm()
                        if picking_id.state == 'assigned':
                            quant_check = False
                            location_check = False
                        
                            for j in picking_id.move_ids_without_package:
                                if not j.product_uom_qty == j.reserved_availability:
                                    quant_check = True
                                    _logger.info("Quant Check Failed==============================================> ")
                                    break

                            for k in picking_id.move_line_ids_without_package:
                                if not picking_id.location_id.id == k.location_id.id or not picking_id.location_dest_id.id == k.location_dest_id.id:
                                    location_check = True
                                    _logger.info("Location Check Failed==============================================> ")
                                    break

                            if not quant_check and not location_check:
                                _logger.info("Transfer Moved To Done==============================================> ")
                                picking_id.action_set_quantities_to_reservation()
                                picking_id.button_validate()

                        return {'Status': 200,'record_id':picking_id.name}

            except Exception as e:
                _logger.error("Error==============================================> " + str(e))
                response = {'Status': 503,'Reason':str(e)}
                self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='internal_transfer',response=str(response))
                return response
        else:
            _logger.info("From Location or To Location or Product List Is Missing==============================================>")
            response = {'Status': 400,'Reason':'From Location or To Location or Product List Is Missing'}
            self.create_error_logs(mocdoc_api_values=kw,api_type='create',model='internal_transfer',response=str(response))
            return response
