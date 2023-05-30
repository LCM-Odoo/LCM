from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    inv_insurance_provider_id = fields.Many2one('insurance.provider',string="Insurance Company",copy=False)
    inv_agreed_amount = fields.Float(string="Agreed Amount",copy=False)
    inv_actual_paid = fields.Float(string="Actual Paid",copy=False)
    inv_moc_doc_ref = fields.Char(string="Moc Doc Ref",copy=False)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    moc_doc_ref = fields.Char(string="Moc Doc Ref",copy=False)

