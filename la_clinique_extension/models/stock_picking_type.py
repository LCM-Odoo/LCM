from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

from odoo.tools.float_utils import float_round

import json
from lxml import etree


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_pharm_receipt = fields.Boolean(string='Is Pharm Receipt')
    is_ot_receipt = fields.Boolean(string='Is OT Receipt')



   