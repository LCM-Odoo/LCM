from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError,Warning

from datetime import datetime, timedelta

import json
import requests



class MocdocBills(models.Model):
	_name = 'mocdoc.bills'
	_description = "Mocdoc Bills"
	_inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char(string="Mocdoc Unique Ref")
	model = fields.Selection([('sale', 'Sale'), ('purchase','Purchase'), ('customer','Customer'), ('product','Product'),('payment','Payment'), ('internal_transfer','Internal Transfer')], string='Model', copy=False, tracking=True)
	mocdoc_json_values = fields.Text(string="Mocdoc Json Values",tracking=True)
	sale_order_id = fields.Many2one('sale.order',string='sale order')

	# def send_mail_notifictaion(self,status_code='',response=''):
	#   try:
	#       mail_template = self.env.ref('la_clinique_extension.email_template_doc_details_api')
	#       previous_day = datetime.now() - timedelta(days=1)
	#       date = previous_day.strftime("%Y%m%d")
	#       mail_template.subject = str(date) + ' - '+ 'Doctor Details API'+ ' - Status code : '+ str(status_code)
	#       body = ('Hi Team' + "<br>" 'Kinldy Look into the below' + "<br>" +'Status Code : '+str(status_code) + "<br>" + 'Values :' +str(response)
	#           )
	#       mail_template.with_user(2).body_html = body
	#       mail_id = mail_template.with_user(2).send_mail(False, force_send=True)
	#       _logger.info("Mail Status==============================================>" + str(mail_id))
	#       return True
	#   except Exception as e:
	#       _logger.error("Error in Sending Mail==============================================> " + str(e))
	#       return False


	# def get_doc_bill_details(self):
	#   if not self.bill_date:raise ValidationError('Kinldy Provide The Bill date')
	#   if not self.bill_location:raise ValidationError('Kinldy Provide The Bill Location')
	#   self.fetch_bill_details(from_config=True)


	# def make_api_post_request(self,url, headers, body):
	#   try:
	#       response = requests.post(url, headers=headers, data=body)
	#       _logger.info("Response==============================================>" + str(response))
	#       if response and response.status_code == 200:
	#           _logger.info("JSON Response==============================================>" + str(response.json()))
	#           self.send_mail_notifictaion(status_code=str(response.status_code),response=str(response.json()))
	#           return response.json()
	#       else:
	#           self.send_mail_notifictaion(status_code=str(response.status_code),response=str(response.json()))
	#           _logger.info("No Data Found==============================================>")
	#           return False
	#   except Exception as e:
	#       self.send_mail_notifictaion(response=str(e))
	#       _logger.error("Error==============================================> " + str(e))
	#       return None


	# def fetch_bill_details(self,from_config=False):
	#   if from_config:
	#       date = self.bill_date.strftime("%Y%m%d")
	#       api_date = self.bill_date
	#   else:
	#       _logger.info("Cron Current Date==============================================>" +str(datetime.now()))
	#       _logger.info("Prevoius Day==============================================>" +str(datetime.now() - timedelta(days=1)))
	#       previous_day = datetime.now() - timedelta(days=1)
	#       date = previous_day.strftime("%Y%m%d")
	#       api_date = previous_day

	#   api_url = self.url

	#   api_headers = {
	#       "Authorization": self.auth_key,
	#       "date": self.auth_date,
	#       "Content-Type": self.content_type
	#   }

	#   api_body = {
	#       "date": date,
	#       "entitylocation": self.bill_location,
	#   }

	#   response_data = self.make_api_post_request(api_url, api_headers, api_body)
	#   if response_data:
	#       self.env['doctor.details'].update_doctor_details(json_dict=response_data,api_date=api_date)


	# def fetch_bill_details_from_cron(self):
	#   config_id = self.env['doctor.api.config'].search([('active','=',True)],limit=1)
	#   if config_id:
	#       config_id.fetch_bill_details()
	#   else:
	#       _logger.info("No Configuration has been activated==============================================>")




