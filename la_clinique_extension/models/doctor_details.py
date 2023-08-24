from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError,Warning

from datetime import datetime, timedelta

import json
import requests



class DoctorApiConfig(models.Model):
	_name = 'doctor.api.config'
	_description = "Doctor API Config"
	_inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char(string="Name")
	url = fields.Char(string='Url')
	auth_key = fields.Char(string='API Authorization Key') 
	auth_date = fields.Char(string='API Authorization Date') 
	content_type = fields.Char(string='Content Type',default='application/x-www-form-urlencoded') 
	bill_date = fields.Date(string='Bill Date')
	bill_location = fields.Char(string='Bill Location')
	active = fields.Boolean(string="Active", default=True)


	def btn_active(self):
		return self.write({'active': True})

	def btn_deactive(self):
		return self.write({'active': False})

	# def test_connection(self,from_config=True):
	# 	if self.active:
			

	def get_doc_bill_details(self):
		if not self.bill_date:raise ValidationError('Kinldy Provide The Bill date')
		if not self.bill_location:raise ValidationError('Kinldy Provide The Bill Location')
		self.fetch_bill_details(from_config=True)



	def make_api_post_request(self,url, headers, body):
		try:
			response = requests.post(url, headers=headers, data=body)
			_logger.info("Response==============================================>" + str(response))
			if response and response.status_code == 200:
				_logger.info("JSON Response==============================================>" + str(response.json()))
				return response.json()
			else:
				_logger.info("No Data Found==============================================>")
				return False

		except Exception as e:
			_logger.error("Error==============================================> " + str(e))
			return None


	def fetch_bill_details(self,from_config=False):
		if from_config:
			date = self.bill_date.strftime("%Y%m%d")
		else:
			_logger.info("Cron Current Date==============================================>" +str(datetime.now()))
			_logger.info("Prevoius Day==============================================>" +str(datetime.now() - timedelta(days=1)))
			previous_day = datetime.now() - timedelta(days=1)
			date = previous_day.strftime("%Y%m%d")

		api_url = self.url

		api_headers = {
			"Authorization": self.auth_key,
			"date": self.auth_date,
			"Content-Type": self.content_type
		}

		api_body = {
			"date": date,
			"entitylocation": self.bill_location,
		}

		response_data = self.make_api_post_request(api_url, api_headers, api_body)
		if response_data:
			self.env['doctor.details'].update_doctor_details(json_dict=response_data)


	def fetch_bill_details_from_cron(self):
		config_id = self.env['doctor.api.config'].search([('active','=',True)],limit=1)
		if config_id:
			config_id.fetch_bill_details()
		else:
			_logger.info("No Configuration has been activated==============================================>")





class DoctorDetails(models.Model):
	_name = 'doctor.details'
	_description = "Doctor Details"
	_inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
	_order = 'bill_date desc'


	name = fields.Char(string="Dept")
	bill_ref = fields.Char(string="Bill Ref")
	patient_name = fields.Char(string='Patient')
	total_bill_amount = fields.Float(string='Payment Amt')
	total_sale_amount = fields.Float(string='Sale Amt')
	outstanding_amount = fields.Float(string='Outstanding Amt')
	bill_date = fields.Date(string='Bill Date')
	doctor = fields.Char(string='Doctor')
	doc_fee = fields.Float(string='Doc Fees charged')
	doc_status = fields.Selection([('paid', 'Paid')], string='Doc Status', default='')
	doc_paid_date = fields.Datetime(string='Doc Paid Date')
	doa = fields.Datetime(string='Date Of Admission')
	dod = fields.Datetime(string='Date Of Discharge')
	ins_provider_id = fields.Many2one('insurance.provider',string="Ins Prov",copy=False)
	ins_agreed_amount = fields.Float(string="Ins Agreed Amount",copy=False)
	ins_actual_paid = fields.Float(string="Ins Actual Paid",copy=False)
	reason = fields.Char(string='Reason')
	sale_order_id = fields.Many2one('sale.order',string='Sale Order',copy=False)
	# invoice_ids = fields.Many2many('account.move',string='Invoices',related='sale_order_id.invoice_ids',copy=False)


	@api.onchange('doc_status')
	def onchange_doc_status(self):
		if not self.doc_status:
			self.doc_paid_date = ''



	def update_doctor_details(self,json_dict=False):
		if json_dict.get('billinglist_detailed'):
			_logger.info("Json Dict==============================================>" + str(json_dict.get('billinglist_detailed')))
			for i in json_dict.get('billinglist_detailed'):
				if i.get('dept') == 'CONSULTATION':
					bill_date = datetime.strptime(i.get('billdate'), "%Y%m%d%H:%M:%S")

					doc_detail_id = self.env['doctor.details'].create(
						{
							'name': i.get('dept'),
							'patient_name': i.get('name'),
							'bill_ref': i.get('bill_no'),
							'doctor': i.get('subdept'),
							'doc_fee': i.get('amt'),
							'bill_date': bill_date.date()
						})
					if doc_detail_id:
						doc_detail_id.update_sale_deatils()

	def update_sale_deatils(self):
		if self.bill_ref:
			_logger.info("Bill Ref==============================================>" + str(self.bill_ref))
			sale_id = self.env['sale.order'].search([('moc_doc_ref','=',self.bill_ref),('state','!=','cancel')])
			_logger.info("Sale Id==============================================>" + str(sale_id))
			if sale_id:
				if len(sale_id) == 1:
					pay_amount = 0.0
					reason = 'Sale Created'
					_logger.info("Sale Created On Odoo==============================================>")
					sale_amount = sale_id.amount_total
					for inv in sale_id.invoice_ids:
						if inv.move_type == 'out_invoice' and inv.state =='posted':
							reason = 'Invoice Posted'
							_logger.info("Invoice Posted On Odoo==============================================>")
							if inv.invoice_payments_widget and json.loads(inv.invoice_payments_widget) and json.loads(inv.invoice_payments_widget).get('content'):
								for j in json.loads(inv.invoice_payments_widget).get('content'):
									pay_amount +=  j.get('amount') if j.get('account_payment_id') else 0.0

					self.write(
						{
							'total_bill_amount':pay_amount,
							'total_sale_amount':sale_amount,
							'outstanding_amount': sale_amount - pay_amount,
							'ins_provider_id':sale_id.insurance_provider_id.id,
							'ins_agreed_amount':sale_id.agreed_amount,
							'ins_actual_paid':sale_id.actual_paid,
							'reason':reason,
							'sale_order_id':sale_id.id,
						})
				else:
					sale_list = [i.name for i in sale_id]
					_logger.info("More than one Sale Bill has been found==============================================>" + str(sale_list))
					self.reason = 'More than one Sale Bill has been found' + str(sale_list)
			else:
				_logger.info("Sale Not Created On Odoo==============================================>")
				self.total_bill_amount = 0.0
				self.total_sale_amount = 0.0
				self.outstanding_amount = 0.0
				self.ins_provider_id = False
				self.sale_order_id = False
				self.ins_agreed_amount = 0.0
				self.ins_actual_paid = 0.0
				self.reason = 'Sale Not Created On Odoo'	

	def action_update_nielsen_image(self):
		count = 0
		for i in self:
			count = count+1
			_logger.info("==============================================>Count=========================================================> {x}".format(x=str(count)))
			i.update_sale_deatils()
			

