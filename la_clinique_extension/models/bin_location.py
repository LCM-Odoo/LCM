from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class BinLocation(models.Model):
    _name = 'bin.location'
    _description = "Bin Location Master"
    _inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
    _order = 'id desc'


    name = fields.Char(string="Name",tracking=True)
    code = fields.Char(string="Code",tracking=True)

    _sql_constraints = [('unique_name','UNIQUE(name)', 'Name already exist.'),('unique_code','UNIQUE(code)', 'Code already exist.')]
