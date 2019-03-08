# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10nEsBfaMod140LineTaxSummary(models.Model):
    _name = "l10n.es.bfa.mod140.line.tax.summary"
    _inherit = 'l10n.es.bfa.mod140.line.summary'

    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Account Tax',
        required=True, ondelete="cascade")
