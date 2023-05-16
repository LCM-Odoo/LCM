from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    create_api_values = fields.Char(string='Create API Values',copy=False)
    make_po_readonly = fields.Boolean(string='Make PO Readonly',copy=False)


