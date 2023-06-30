from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    brn = fields.Char(string='BRN',copy=False)
    national_id = fields.Char(string='NID',copy=False)
    moc_doc_id = fields.Char(string='Moc Doc Id',copy=False)
    doctor = fields.Char(string='Doctor',copy=False)
    diagnosis = fields.Char(string='Diagnosis',copy=False)
    # is_cash_customer = fields.Boolean(string='Is Cash Customer',copy=False)
    create_api_values = fields.Char(string='Create API Values',copy=False)
    write_api_values = fields.Char(string='Write API Values',copy=False)



    @api.model
    def create(self, vals):
        context = dict(self._context)
        result = super(ResPartner, self).create(vals)
        return result
