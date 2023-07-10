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





