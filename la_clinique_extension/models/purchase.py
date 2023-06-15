from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    create_api_values = fields.Char(string='Create API Values',copy=False)
    make_po_readonly = fields.Boolean(string='Make PO Readonly',copy=False)
    moc_doc_ref = fields.Char(string="Moc Doc Ref",copy=False)

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals['inv_moc_doc_ref'] = self.moc_doc_ref if self.moc_doc_ref else False
        return invoice_vals





