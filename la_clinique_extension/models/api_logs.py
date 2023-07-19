from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)

import json



class ApiLogs(models.Model):
    _name = 'api.logs'
    _description = "API Logs Master"
    _inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
    _order = 'id desc'


    name = fields.Text(string="Error Response",tracking=True)
    mocdoc_api_values = fields.Text(string="Mocdoc Api Values",tracking=True)
    model = fields.Selection([('sale', 'Sale'), ('purchase','Purchase'), ('customer','Customer'), ('product','Product'),('payment','Payment'), ('internal_transfer','Internal Transfer')], string='Model', copy=False, tracking=True)
    api_type = fields.Selection([('create', 'Create'), ('update','Update')], string='Type', copy=False, tracking=True)
    moc_doc_ref = fields.Char(string='Moc Doc Ref', copy=False, tracking=True)
    product_list = fields.Html(string='Product List', copy=False, tracking=True)
    del_skip_reason = fields.Text(string="Delete Skip Response",tracking=True)


    def send_mail_to_clinet(self,mocdoc_api_values='',api_type='',model='',response=''):
        context = dict(self._context or {})
        if self.model == 'customer':
            mail_template = self.env.ref('la_clinique_extension.customer_api_email_template')
            mail_template.send_mail(self.id, force_send=True)

        elif self.model == 'product':
            mail_template = self.env.ref('la_clinique_extension.product_api_email_template')
            mail_template.send_mail(self.id, force_send=True)

        elif self.model == 'sale':
            mail_template = self.env.ref('la_clinique_extension.sale_api_email_template')
            if self.moc_doc_ref:
                subject = 'Mocdoc - Sale Bill Error - ' + self.moc_doc_ref
            else:
                subject = 'Mocdoc - Sale Bill Error'

            mail_template.subject = subject
            mail_template.send_mail(self.id, force_send=True)

        elif self.model == 'purchase':
            mail_template = self.env.ref('la_clinique_extension.purchase_api_email_template')
            if self.moc_doc_ref:
                subject = 'Mocdoc - Purchase Bill Error - ' + self.moc_doc_ref
            else:
                subject = 'Mocdoc - Purchase Bill Error'

            mail_template.subject = subject
            mail_template.send_mail(self.id, force_send=True)

        elif self.model == 'payment':
            mail_template = self.env.ref('la_clinique_extension.payment_api_email_template')
            mail_template.send_mail(self.id, force_send=True)

        elif self.model == 'internal_transfer':
            mail_template = self.env.ref('la_clinique_extension.internal_transfer_api_email_template')
            mail_template.send_mail(self.id, force_send=True)


    def remove_log_records(self):
        api_logs = self.env['api.logs'].search([])
        if api_logs:
            _logger.info("Total API Logs==============================================>" + str(api_logs))
            count=0
            for i in api_logs:
                count+=1
                _logger.info("Log Count==============================================>" + str(count))

                moc_doc_ref = i.mocdoc_api_values.replace("'", "\"")
                json_dict = json.loads(moc_doc_ref)


                # if i.model == 'product':
                #     _logger.info("Product Log==============================================>")

                #     product_id = self.env['product.template'].search([('default_code','=',json_dict.get('default_code'))])
                #     if product_id:
                #         i.unlink()
                #         _logger.info("Record Removed==============================================>" + str(count))
                #     else:
                #         _logger.info("Record Stays==============================================>" + str(count))

                if i.model == 'sale':
                    _logger.info("Sale Log==============================================>")
                    if json_dict.get('moc_doc_ref'):
                        sale_order_id = self.env['sale.order'].search([('state','!=','cancel'),('moc_doc_ref','=',json_dict.get('moc_doc_ref'))])
                        if sale_order_id:
                            if len(sale_order_id) == 1:
                                i.unlink()
                                _logger.info("Sale Record Removed==============================================>" + str(sale_order_id))
                            else:
                                 _logger.info("More Than 2 Sale Records==============================================>" + str(sale_order_id))
                        else:
                            _logger.info("Sale Record Stays==============================================>" + str(count))
                    else:
                        _logger.info("No Moc doc Ref for the Bill==============================================>")

                elif i.model == 'purchase':
                    _logger.info("Purchase Log==============================================>")
                    if json_dict.get('moc_doc_ref'):
                        purchase_order_id = self.env['purchase.order'].search([('state','!=','cancel'),('moc_doc_ref','=',json_dict.get('moc_doc_ref'))])
                        if purchase_order_id:
                            if len(purchase_order_id) == 1:
                                i.unlink()
                                _logger.info("Purchase Record Removed==============================================>" + str(purchase_order_id))
                            else:
                                 _logger.info("More Than 2 Purchase Records==============================================>" + str(purchase_order_id))
                        else:
                            _logger.info("Purchase Record Stays==============================================>" + str(count))
                    else:
                        _logger.info("No Moc doc Ref for the Bill==============================================>")





