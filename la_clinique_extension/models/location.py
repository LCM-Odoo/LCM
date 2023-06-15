from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_missing_loc = fields.Boolean(string='Is Missing API Location',copy=False)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_api_transfer = fields.Boolean(string='Is API Transfer',copy=False)


