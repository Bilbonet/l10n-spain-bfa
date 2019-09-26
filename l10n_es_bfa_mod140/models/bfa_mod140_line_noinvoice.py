# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10nEsBfaMod140LineNoInvoice(models.Model):
    _name = "l10n.es.bfa.mod140.line.noinvoice"
    _description = "BFA Modelo 140 expenses without invoice"

    mod140_id = fields.Many2one(
        comodel_name='l10n.es.bfa.mod140',
        string='Modelo 140 id', ondelete='cascade')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry')
    move_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Journal Entry Line')
    ref = fields.Char('Reference')
    date = fields.Date(
        string='Expense Date')
    account_pgc = fields.Integer(string='Account in the PGC', readonly='True')
    amount = fields.Float(string='Expense amount')
    exception = fields.Boolean(string="Exception")
    exception_text = fields.Char(string="Exception text")
