from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessError, UserError, ValidationError



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    create_api_values = fields.Char(string='Create API Values',copy=False)
    make_po_readonly = fields.Boolean(string='Make PO Readonly',copy=False)
    moc_doc_ref = fields.Char(string="Moc Doc Ref",copy=False)

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals['inv_moc_doc_ref'] = self.moc_doc_ref if self.moc_doc_ref else False
        return invoice_vals

    def action_create_invoice(self):
        for order in self:
            if order.create_api_values:
                for line in order.order_line:
                    if not line.taxes_id:
                        raise UserError(_('The Tax Is Not Mapped for the Product: %s , Kinldy Map It.' % (line.product_id.name)))
        values = super(PurchaseOrder, self).action_create_invoice()
        return values






