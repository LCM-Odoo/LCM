from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    create_api_values = fields.Char(string='Create API Values',copy=False)
    make_so_readonly = fields.Boolean(string='Make SO Readonly',copy=False)
    moc_doc_ref = fields.Char(string="Moc Doc Ref",copy=False)

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

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['inv_insurance_provider_id'] = self.insurance_provider_id.id if self.insurance_provider_id else ''
        invoice_vals['inv_agreed_amount'] = self.agreed_amount if self.agreed_amount else 0.0
        invoice_vals['inv_actual_paid'] = self.actual_paid if self.actual_paid else 0.0
        return invoice_vals






