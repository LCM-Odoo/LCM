from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class ProductPricleist(models.Model):
    _inherit = 'product.pricelist'

    is_moc_doc_priclist = fields.Boolean(string="Is MocDoc Pricelist",copy=False)

