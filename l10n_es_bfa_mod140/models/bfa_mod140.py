# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from calendar import monthrange
from odoo import _, api, fields, exceptions, models
from odoo.tools import config
from datetime import datetime
from odoo.exceptions import Warning as UserError


class L10nEsBfaMod140(models.Model):
    _name = "l10n.es.bfa.mod140"
    _description = "BFA Modelo 140 Módulo Declaración"
    # _rec_name = 'name'
    _period_quarterly = True
    _period_monthly = True
    _period_yearly = True

    def _default_year(self):
        return fields.Date.from_string(fields.Date.today()).year

    def get_period_type_selection(self):
        period_types = []
        if self._period_yearly or config['test_enable']:
            period_types += [('0A', '0A - Anual')]
        if self._period_quarterly:
            period_types += [('1T', '1T - Primer trimestre'),
                             ('2T', '2T - Segundo trimestre'),
                             ('3T', '3T - Tercer trimestre'),
                             ('4T', '4T - Cuarto trimestre')]
        if self._period_monthly or config['test_enable']:
            period_types += [('01', '01 - Enero'),
                             ('02', '02 - Febrero'),
                             ('03', '03 - Marzo'),
                             ('04', '04 - Abril'),
                             ('05', '05 - Mayo'),
                             ('06', '06 - Junio'),
                             ('07', '07 - Julio'),
                             ('08', '08 - Agosto'),
                             ('09', '09 - Septiembre'),
                             ('10', '10 - Octubre'),
                             ('11', '11 - Noviembre'),
                             ('12', '12 - Diciembre')]
        return period_types

    def _default_period_type(self):
        selection = self.get_period_type_selection()
        return selection and selection[0][0] or False

    company_id = fields.Many2one(
        comodel_name='res.company', string="Company", required=True,
        readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(),
        states={'draft': [('readonly', False)]})
    company_vat = fields.Char(
        string="VAT number", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    contact_name = fields.Char(
        string="Full Name", size=40, help="Must have surnames, and name.",
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    contact_phone = fields.Char(
        string="Phone", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    contact_email = fields.Char(
        string="Contact email", size=50, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    representative_vat = fields.Char(
        string="L.R. VAT number", size=9, required=True, readonly=True,
        help="Legal Representative VAT number.",
        states={'draft': [('readonly', False)]})
    representative_name = fields.Char(
        string="L.R. Full Name", size=40, help="Must have surnames, and name.",
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    representative_phone = fields.Char(
        string="L.R. Phone", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    representative_email = fields.Char(
        string="L.R. Contact email", size=50, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    year = fields.Integer(
        string="Year", default=_default_year, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    calculation_date = fields.Datetime(string="Calculation date")
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('calculated', 'Processed'),
            ('done', 'Done'),
            ('posted', 'Posted'),
            ('cancelled', 'Cancelled'),
        ], string='State', default='draft', readonly=True)
    name = fields.Char(string="Report Name", size=13, required=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string="Currency", readonly=True,
        related='company_id.currency_id')
    period_type = fields.Selection(
        selection='get_period_type_selection', string="Period type",
        required=True, default=_default_period_type,
        readonly=True, states={'draft': [('readonly', False)]})
    date_start = fields.Date(
        string="Starting date", required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    date_end = fields.Date(
        string="Ending date", required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Partner",
        related='company_id.partner_id', readonly=True)

    line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        string='Issued/Received invoices',
        copy=False,
        readonly="True")
    issued_line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        domain=[('line_type', '=', 'issued')],
        string='Issued invoices',
        copy=False,
        readonly="True")
    rectification_issued_line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        domain=[('line_type', '=', 'rectification_issued')],
        string='Issued Refund Invoices',
        copy=False,
        readonly="True")
    received_line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        domain=[('line_type', '=', 'received')],
        string='Received invoices',
        copy=False,
        readonly="True")
    rectification_received_line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        domain=[('line_type', '=', 'rectification_received')],
        string='Received Refund Invoices',
        copy=False,
        readonly="True")

    summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line.summary',
        string="Summary",
        inverse_name='mod140_id',
        readonly="True")
    issued_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line.summary',
        string="Issued Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'issued')],
        readonly="True")
    received_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line.summary',
        string="Received Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'received')],
        readonly="True")

    tax_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line.tax.summary',
        string="Tax Summary",
        inverse_name='mod140_id',
        readonly="True")
    issued_tax_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line.tax.summary',
        string="Issued Tax Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'issued')],
        readonly="True")
    received_tax_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line.tax.summary',
        string="Received Tax Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'received')],
        readonly="True")

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)',
         'BFA report identifier must be unique'),
    ]

    @api.onchange('company_id')
    def onchange_company_id(self):
        """Load some company data (the VAT number) when company changes.
        """
        if self.company_id.vat:
            # Remove the ES part from spanish vat numbers
            #  (ES12345678Z => 12345678Z)
            self.company_vat = re.match(
                "(ES){0,1}(.*)", self.company_id.vat).groups()[1]
        self.contact_name = self.env.user.name
        self.contact_email = self.env.user.email
        self.contact_phone = self._filter_phone(
            self.env.user.partner_id.phone or
            self.env.user.partner_id.mobile or
            self.env.user.company_id.phone)

    @api.onchange('year', 'period_type')
    def onchange_period_type(self):
        if not self.year or not self.period_type:
            self.date_start = False
            self.date_end = False
        else:
            if self.period_type == '0A':
                # Anual
                self.date_start = fields.Date.from_string(
                    '%s-01-01' % self.year)
                self.date_end = fields.Date.from_string(
                    '%s-12-31' % self.year)
            elif self.period_type in ('1T', '2T', '3T', '4T'):
                # Trimestral
                starting_month = 1 + (int(self.period_type[0]) - 1) * 3
                ending_month = starting_month + 2
                self.date_start = fields.Date.from_string(
                    '%s-%s-01' % (self.year, starting_month))
                self.date_end = fields.Date.from_string(
                    '%s-%s-%s' % (
                        self.year, ending_month,
                        monthrange(self.year, ending_month)[1]))
            elif self.period_type in ('01', '02', '03', '04', '05', '06',
                                      '07', '08', '09', '10', '11', '12'):
                # Mensual
                month = int(self.period_type)
                self.date_start = fields.Date.from_string(
                    '%s-%s-01' % (self.year, month))
                self.date_end = fields.Date.from_string('%s-%s-%s' % (
                    self.year, month, monthrange(self.year, month)[1]))

    @api.multi
    def calculate(self):
        self.write({'state': 'calculated',
                    'calculation_date': fields.Datetime.now()})
        """
            Funcion call from mod140
        """
        self._calculate_mod140()
        return True

    def _clear_old_data(self):
        """
            This function clean all the old data to make a new calculation
        """
        self.line_ids.unlink()
        self.summary_ids.unlink()
        self.tax_summary_ids.unlink()

    def _calculate_mod140(self):
        """
            This function calculate all the taxes, from issued invoices,
            received invoices and rectification invoices
        """
        for rec in self:
            if not rec.company_id.partner_id.vat:
                raise UserError(
                    _("This company doesn't have VAT"))

            # clean the old records
            rec._clear_old_data()

            tax_model = self.env['account.tax']
            # Obtain all the codes from account.tax.template
            codes_issued = self.env['account.tax.template'].filtered(
                lambda t: t.type_tax_use == 'sale').mapped('description')
            codes_issued = self.env['account.tax.template'].filtered(
                lambda t: t.type_tax_use == 'purchase').mapped('description')


            # # search the account.tax referred to by the template
            # taxes_issued = tax_model.search(
            #     [('description', 'in', codes_issued),
            #      ('company_id', 'child_of', rec.company_id.id)])
            # taxes_received = tax_model.search(
            #     [('description', 'in', codes_received),
            #      ('company_id', 'child_of', rec.company_id.id)])

    @api.model
    def _filter_phone(self, phone):
        return (phone or '').replace(" ", "")[-9:]
