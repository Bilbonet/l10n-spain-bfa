# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10nEsBfaMod140Summary(models.Model):
    _name = "l10n.es.bfa.mod140.summary"

    mod140_id = fields.Many2one(
        comodel_name='l10n.es.bfa.mod140',
        string='Modelo 140 id', ondelete='cascade')

    book_type = fields.Selection(selection=[
        ('issued', 'Issued'),
        ('received', 'Received'),
    ], string='Book type')

    base_amount = fields.Float(
        string='Base amount',
        readonly="True")

    tax_amount = fields.Float(
        string='Tax amount',
        readonly="True")

    total_amount = fields.Float(
        string='Total amount',
        readonly="True")
