from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    create_api_values = fields.Char(string='Create API Values',copy=False)
    make_so_readonly = fields.Boolean(string='Make SO Readonly',copy=False)

    insurance_provider_id = fields.Many2one('insurance.provider',string="Insurance Company",copy=False)
    agreed_amount = fields.Float(string="Agreed Amount",copy=False)
    actual_paid = fields.Float(string="Actual Paid",copy=False)


    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        return result

    def write(self, values):
        result = super(SaleOrder, self).write(values)
        return result




