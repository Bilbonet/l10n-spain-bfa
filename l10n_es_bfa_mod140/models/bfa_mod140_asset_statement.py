# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10nEsBfaMod140AssetStatement(models.Model):
    _name = "l10n.es.bfa.mod140.asset.statement"
    _description = "BFA Modelo 140 Assets in the statement"

    mod140_id = fields.Many2one(
        comodel_name='l10n.es.bfa.mod140',
        string='Modelo 140 id', ondelete='cascade')
    asset_id = fields.Many2one(
        comodel_name='l10n.es.bfa.mod140.asset',
        string='Asset Name')
    ref = fields.Char(related='asset_id.ref',
                      strig='Asset Reference', readonly=True)
    export = fields.Boolean(
        string="Export", default=True,
        help='You can decide if export the asset in the export '
             'file for BFA declaration')
    exception = fields.Boolean(string="Exception")
    exception_text = fields.Char(string="Exception text")
