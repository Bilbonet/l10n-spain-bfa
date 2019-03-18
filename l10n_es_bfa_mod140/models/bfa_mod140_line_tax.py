# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class L10nEsBfaMod140LineTax(models.Model):
    _name = "l10n.es.bfa.mod140.line.tax"
    _description = "BFA Modelo 140 Tax lines"

    mod140_line_id = fields.Many2one(comodel_name='l10n.es.bfa.mod140.line',
                                     required=True, ondelete='cascade')
    base_amount = fields.Float(string='Base')
    tax_id = fields.Many2one(comodel_name='account.tax', string='Tax')
    tax_rate = fields.Float(string='Tax Rate (%)', compute='_compute_tax_rate')
    tax_amount = fields.Float(string='Tax fee')
    total_amount = fields.Float(string='Total')
    move_line_ids = fields.Many2many(
        comodel_name='account.move.line', string='Move Lines')
    account_pgc = fields.Integer(string='Account in the PGC', readonly='True')

    @api.multi
    @api.depends('tax_id')
    def _compute_tax_rate(self):
        for rec in self:
            rec.tax_rate = rec.tax_id.amount
