from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    create_api_values = fields.Char(string='Create API Values',copy=False)
    write_api_values = fields.Char(string='Write API Values',copy=False)

    bin_location_id = fields.Many2one('bin.location',string='Bin Location',copy=False)
    product_profile_id = fields.Many2one('product.profile',string='Product Profile',copy=False)



