from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class ApiLogs(models.Model):
    _name = 'api.logs'
    _description = "API Logs Master"
    _inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
    _order = 'id desc'


    name = fields.Text(string="Error Response",tracking=True)
    mocdoc_api_values = fields.Text(string="Mocdoc Api Values",tracking=True)
    model = fields.Selection([('sale', 'Sale'), ('purchase','Purchase'), ('customer','Customer'), ('product','Product'),('payment','Payment'), ('internal_transfer','Internal Transfer')], string='Model', copy=False, tracking=True)
    api_type = fields.Selection([('create', 'Create'), ('update','Update')], string='Type', copy=False, tracking=True)


