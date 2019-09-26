# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    use_mod140_asset = fields.Boolean(related='journal_id.use_mod140_asset',
                                      readonly=True,)
    mod140_asset_id = fields.Many2one(comodel_name='l10n.es.bfa.mod140.asset',
                                      string='BFA Model 140 Asset',
                                      copy=False)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.use_mod140_asset:
            self.mod140_asset_id = ''
