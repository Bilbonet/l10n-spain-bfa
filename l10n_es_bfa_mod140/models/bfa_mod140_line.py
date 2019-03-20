# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class L10nEsBfaMod140Line(models.Model):
    _name = "l10n.es.bfa.mod140.line"
    _description = "BFA Modelo 140 Invoices"
    _order = 'ref asc, invoice_date asc'

    mod140_id = fields.Many2one(
        comodel_name='l10n.es.bfa.mod140',
        string='Modelo 140 id', ondelete='cascade')
    line_type = fields.Selection(selection=[
        ('issued', 'Issued'),
        ('received', 'Received'),
        ('rectification_issued', 'Refund Issued'),
        ('rectification_received', 'Refund Received')],
        string='Line type')
    ref = fields.Char('Reference')
    external_ref = fields.Char('External Reference')
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry')
    invoice_date = fields.Date(
        string='Invoice Date')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Empresa')
    vat_number = fields.Char(
        string='NIF')
    tax_line_ids = fields.One2many(comodel_name='l10n.es.bfa.mod140.line.tax',
                                   inverse_name='mod140_line_id',
                                   string='Tax Lines', copy=False)
    operation_type = fields.Char(string="Operation type")
    register_type = fields.Char(string="Register type")
    special_operation = fields.Char(string="Special operation")
    key_nif = fields.Selection(selection=[
        ('1', 'NIF'),
        ('2', 'NIF intracommunity')],
        string='Key identification. Type of identification document')
    exception = fields.Boolean(string="Exception")
    exception_text = fields.Char(string="Exception text")

    @api.multi
    @api.depends('tax_id')
    def _compute_tax_rate(self):
        for rec in self:
            rec.tax_rate = rec.tax_id.amount
