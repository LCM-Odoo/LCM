from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_mcb_journal = fields.Boolean(string='Is MCB Card Journal',copy=False)
    is_sbm_journal = fields.Boolean(string='Is SBM Card Journal',copy=False)





