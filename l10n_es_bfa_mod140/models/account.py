# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = ['account.journal']

    use_mod140_asset = fields.Boolean(string="Use BFA model 140 asset",
                                      default=False)

    @api.onchange('type')
    def _onchange_type(self):
        if self.type not in ['purchase']:
            self.use_mod140_asset = False
