from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class InsuranceProvider(models.Model):
    _name = 'insurance.provider'
    _description = "Insurance Provider Master"
    _inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Name',copy=False)
    code = fields.Char(string='Code',copy=False)
    active = fields.Boolean(string='active',default=True)

    _sql_constraints = [('unique_name','UNIQUE(name)', 'Name already exist.'),('unique_code','UNIQUE(code)', 'Code already exist.')]  


   