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
    _description = "BFA Modelo 140 Statement module"
    _rec_name = 'name'
    _period_quarterly = True
    _period_monthly = True
    _period_yearly = True
    _bfa_number = '140'

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

    def _default_number(self):
        return self._bfa_number

    def _get_export_config(self, date):
        model = self.env['ir.model'].search([('model', '=', self._name)])
        return self.env['aeat.model.export.config'].search([
            ('model_id', '=', model.id),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ], limit=1)

    def _default_export_config_id(self):
        return self._get_export_config(fields.Date.today())

    company_id = fields.Many2one(
        comodel_name='res.company', string="Company", required=True,
        readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(),
        states={'draft': [('readonly', False)]})
    company_vat = fields.Char(
        string="VAT number", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    number = fields.Char(
        string="Model number", size=3, required=True, readonly=True,
        default=_default_number)
    calculation_date = fields.Datetime(string="Calculation date")
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('calculated', 'Processed'),
            ('done', 'Done'),
            ('posted', 'Posted'),
            ('cancelled', 'Cancelled'),
        ], string='State', default='draft', readonly=True)
    name = fields.Char(string="Report Name", size=13)
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
    export_config_id = fields.Many2one(
        comodel_name='aeat.model.export.config', string="Export config",
        domain=lambda self: [
            ('model_id', '=',
             self.env['ir.model'].search([('model', '=', self._name)]).id)
        ],
        default=_default_export_config_id, oldname='export_config')

    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Partner",
        related='company_id.partner_id', readonly=True)
    declarant_name = fields.Char(
        string="Declarant: Surnames, Name", size=40,
        help="Declarant full name, must have surnames, name.",
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    declarant_phone = fields.Char(
        string="Declarant Phone", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    declarant_mobile = fields.Char(
        string="Declarant Mobile", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    declarant_email = fields.Char(
        string="E-mail", size=50, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    representative_vat = fields.Char(
        string="R.VAT number", size=9, readonly=True,
        help="Legal Representative VAT number.",
        states={'draft': [('readonly', False)]})
    representative_name = fields.Char(
        string="R.Surnames, Name", size=40,
        help="Legal Representative full name, must have surnames, name.",
        readonly=True, states={'draft': [('readonly', False)]})
    contact_type = fields.Selection(
        selection=[
            ('D', 'Declarant'),
            ('R', 'Representative'),
            ('O', 'Others'),
        ], string="Contact Type", default='D', readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    contact_name = fields.Char(
        string="Contact: Surnames, Name", size=40,
        help="Contact full name, must have surnames, name.",
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    contact_phone = fields.Char(
        string="Contact Phone", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    contact_mobile = fields.Char(
        string="Contact Mobile", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    contact_email = fields.Char(
        string="Contact email", size=50, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    year = fields.Integer(
        string="Year", default=_default_year, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    type = fields.Selection(
        selection=[
            ('N', 'Normal'),
            ('S', 'Substitutive'),
        ], string="Statement Type", default='N', readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    size = fields.Selection(
        selection=[
            ('M', 'Microempresa'),
            ('P', 'Empresa pequeña'),
        ], string="Company size", default='M', readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    amortization = fields.Boolean(string='Joint amortization', readonly=True,
        default=False,
        help='Applies joint amortization, only for microenterprise',
        states={'draft': [('readonly', False)]})

    epigraph = fields.Char(
        string="Activity epigraph", size=7, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    activity_start = fields.Date(
        string="Activity start date", required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    activity_end = fields.Date(
        string="Activity end date", readonly=True,
        states={'draft': [('readonly', False)]})
    regime_irpf = fields.Selection(
        selection=[
            ('N', 'Directa Normal'),
            ('S', 'Directa Simplificada'),
        ], string="Regime IRPF",
        default='N', readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    eds_irpf = fields.Boolean(string='EDS IRPF', readonly=True,
        default=False,
        help='Charges and payments EDS IRPF',
        states={'draft': [('readonly', False)]})
    reg_general = fields.Boolean(string='General regime', readonly=True,
        default=True, states={'draft': [('readonly', False)]})
    reg_simplified = fields.Boolean(string='Simplified regime', readonly=True,
        default=False, states={'draft': [('readonly', False)]})
    reg_agp = fields.Boolean(
        string='Special regime agriculture livestock fishing', readonly=True,
        default=False, states={'draft': [('readonly', False)]})
    reg_equi = fields.Boolean(string='Equivalence surcharge', readonly=True,
        default=False, states={'draft': [('readonly', False)]})
    reg_cash_criterion = fields.Boolean(
        string='Cash criterion', readonly=True,
        default=False, states={'draft': [('readonly', False)]})
    reg_others = fields.Boolean(
        string='Others special regimes', readonly=True,
        default=False, states={'draft': [('readonly', False)]})
    pro_general = fields.Boolean(
        string='Prorate general', readonly=True,
        default=False, states={'draft': [('readonly', False)]})
    pro_general_percent = fields.Integer(
        string="Prorate general percent", defaul=0,
        help="Prorate general (%)", readonly=True,
        states={'draft': [('readonly', False)]})
    pro_special = fields.Boolean(
        string='Prorate special', readonly=True,
        default=False, states={'draft': [('readonly', False)]})
    all_exempt = fields.Boolean(
        string='All exempt operations', readonly=True,
        default=False, states={'draft': [('readonly', False)]})

    line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        string='Issued/Received invoices',
        copy=False,
        readonly="True")
    all_issued_line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        domain=[('line_type', 'in', ['issued', 'rectification_issued'])],
        string='ALL Issued invoices',
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
    all_received_line_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line',
        inverse_name='mod140_id',
        domain=[('line_type', 'in', ['received', 'rectification_received'])],
        string='All Received invoices',
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
        comodel_name='l10n.es.bfa.mod140.summary',
        string="Summary",
        inverse_name='mod140_id',
        readonly="True")
    issued_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.summary',
        string="Issued Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'issued')],
        readonly="True")
    received_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.summary',
        string="Received Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'received')],
        readonly="True")

    tax_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.tax.summary',
        string="Tax Summary",
        inverse_name='mod140_id',
        readonly="True")
    issued_tax_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.tax.summary',
        string="Issued Tax Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'issued')],
        readonly="True")
    received_tax_summary_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.tax.summary',
        string="Received Tax Summary",
        inverse_name='mod140_id',
        domain=[('book_type', '=', 'received')],
        readonly="True")

    noinvoice_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.line.noinvoice',
        inverse_name='mod140_id',
        string='Expenses without invoice',
        copy=False,
        readonly="True")
    asset_ids = fields.One2many(
        comodel_name='l10n.es.bfa.mod140.asset.statement',
        inverse_name='mod140_id',
        string='Assets in this statement',
        copy=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)',
         'BFA report identifier must be unique'),
        ('pro_general_percent_not_negative', 'CHECK (pro_general_percent>=0)',
         'Prorate general percent cannot be negative.')
    ]

    @api.onchange('company_id')
    def onchange_company_id(self):
        """Load some company data when company changes.
        """
        if self.company_id.vat:
            self.company_vat = self.normalize_vat(self.company_id.vat)

        #Declarant Data
        self.declarant_name = str(self.env.user.partner_id.lastname) + ', ' + \
                              str(self.env.user.partner_id.firstname)
        self.declarant_email = self.env.user.email
        self.declarant_phone = self._filter_phone(
            self.env.user.partner_id.phone or
            self.env.user.partner_id.mobile or
            self.env.user.company_id.phone)
        self.declarant_mobile = self._filter_phone(
            self.env.user.partner_id.mobile or
            self.env.user.partner_id.phone or
            self.env.user.company_id.phone)

        #Contact Data
        self.contact_name = str(self.env.user.partner_id.lastname) + ', ' + \
                            str(self.env.user.partner_id.firstname)
        self.contact_email = self.env.user.email
        self.contact_phone = self._filter_phone(
            self.env.user.partner_id.phone or
            self.env.user.partner_id.mobile or
            self.env.user.company_id.phone)
        self.contact_mobile = self._filter_phone(
            self.env.user.partner_id.mobile or
            self.env.user.partner_id.phone or
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

    @api.onchange('contact_type')
    def onchange_contact_type(self):
        if self.contact_type == 'D':
            self.contact_name = self.declarant_name
            self.contact_phone = self.declarant_phone
            self.contact_mobile = self.declarant_mobile
            self.contact_email = self.declarant_email
        elif self.contact_type == 'R':
            self.contact_name = self.representative_name
        else:
            self.contact_name = ''
            self.contact_phone = ''
            self.contact_mobile = ''
            self.contact_email = ''

    @api.onchange('size')
    def onchange_size(self):
        if self.size == 'P':
            self.amortization = False

    @api.onchange('company_vat', 'representative_vat')
    def onchange_representative_vat(self):
        if self.representative_vat:
            if self.company_vat == self.representative_vat:
                raise exceptions.UserError(_(
                    "Company vat and representative vat can't be equals."
                ))

    @api.onchange('pro_general')
    def onchange_pro_general(self):
        if not self.pro_general:
            self.pro_general_percent = 0

    @api.model
    def _report_identifier_get(self, vals):
        seq_name = "bfa%s-sequence" % self._bfa_number
        company_id = vals.get('company_id', self.env.user.company_id.id)
        seq = self.env['ir.sequence'].search(
            [('name', '=', seq_name), ('company_id', '=', company_id)],
            limit=1,
        )
        if not seq:
            raise exceptions.UserError(_(
                "BFA model sequence not found. You can try to restart your "
                "Odoo service for recreating the sequences."
            ))
        return seq.next_by_id()

    @api.model
    def _prepare_mod140_tax_summary(self, tax_lines, book_type):
        tax_summary_data_recs = {}
        for tax_line in tax_lines:
            if tax_line.tax_id not in tax_summary_data_recs:
                tax_summary_data_recs[tax_line.tax_id] = {
                    'book_type': book_type,
                    'base_amount': 0.0,
                    'tax_amount': 0.0,
                    'total_amount': 0.0,
                    'tax_id': tax_line.tax_id.id,
                    'mod140_id': self.id,
                }
            tax_summary_data_recs[tax_line.tax_id]['base_amount'] += \
                tax_line.base_amount
            tax_summary_data_recs[tax_line.tax_id]['tax_amount'] +=  \
                tax_line.tax_amount
            tax_summary_data_recs[tax_line.tax_id]['total_amount'] +=  \
                tax_line.total_amount
        return tax_summary_data_recs

    @api.model
    def _create_mod140_tax_summary(self, tax_summary_data_recs, tax_summary):
        for tax_id in tax_summary_data_recs.keys():
            self.env['l10n.es.bfa.mod140.tax.summary'].create(
                tax_summary_data_recs[tax_id])
        return tax_summary

    @api.model
    def _prepare_mod140_summary(self, tax_summary_recs, book_type):
        base_amount = sum(tax_summary_recs.mapped('base_amount'))
        tax_amount = sum(tax_summary_recs.mapped('tax_amount'))
        total_amount = sum(tax_summary_recs.mapped('total_amount'))
        return {
            'book_type': book_type,
            'base_amount': base_amount,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'mod140_id': self.id,
        }

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self._report_identifier_get(vals)
        return super(L10nEsBfaMod140, self).create(vals)

    @api.model
    def _create_mod140_summary(self, tax_summary_recs, book_type):
        vals = self._prepare_mod140_summary(tax_summary_recs, book_type)
        self.env['l10n.es.bfa.mod140.summary'].create(vals)

    def _get_vals_invoice_line(self, move, line_type):
        """
            This function make the dictionary to create a new record in issued
            invoices, Received invoices or rectification invoices

            Args:
                move (obj): move

            Returns:
                dictionary: Vals from the new record.
        """
        ref = move.ref
        ext_ref = ''
        invoice = move.line_ids.mapped('invoice_id')[:1]
        partner = move.partner_id
        if invoice:
            partner = invoice.commercial_partner_id
            ref = invoice.number
            ext_ref = invoice.reference
            operation_type = 'A'
            register_type = 'A'
            special_operation = ''
            key_nif = '1'

        if invoice.type == 'out_refund':
            line_type = 'rectification_issued'
        if invoice.type == 'in_refund':
            line_type = 'rectification_received'

        if line_type in ['rectification_issued', 'rectification_received']:
            register_type = 'E'
        # elif len(invoice.tax_line_ids) > 1:
        #     register_type = 'B'  #Varios tipos impositivos/cuentas PGC

        """
            Some values depends on the tax type.
            We search in the map taxes of the model
        """
        # Obtain Map code template from mod140.
        tax_code_map = self.env['l10n.es.aeat.map.tax'].search(
            [('model', '=', '140'),
             '|',
             ('date_from', '<=', self.date_start),
             ('date_from', '=', False),
             '|',
             ('date_to', '>=', self.date_end),
             ('date_to', '=', False)], limit=1)
        # Taxes codes of the invoice
        taxes_codes = move.line_ids.mapped('tax_line_id').mapped('description')

        # Different tax types in the invoice
        map_codes = tax_code_map.map_line_ids.mapped(
            'tax_ids').mapped('description')
        same_values = set(taxes_codes) & set(map_codes)
        if len(same_values) > 1:
            register_type = 'B'

        #ISP: Obtain all the codes with ISP from map taxes
        #Compare ISP codes with move tax codes
        map_codes = tax_code_map.map_line_ids.filtered(
            lambda t: t.field_number in [2, 10, 11]).mapped(
            'tax_ids').mapped('description')
        same_values = set(taxes_codes) & set(map_codes)
        if same_values:
            special_operation = 'I'

        # Intracomunitari Received
        if line_type in ['received', 'rectification_received']:
            # Compare Intracomunitari codes with move tax codes
            map_codes = tax_code_map.map_line_ids.filtered(
                lambda t: t.field_number in [9, 11]).mapped(
                'tax_ids').mapped('description')
            same_values = set(taxes_codes) & set(map_codes)
            if same_values:
                special_operation = 'P'
                key_nif = '2'  # Identification key: Intracomunitari

        return {
            'mod140_id': self.id,
            'line_type': line_type,
            'ref': ref,
            'external_ref': ext_ref,
            'invoice_id': invoice.id,
            'move_id': move.id,
            'invoice_date': move.date,
            'partner_id': partner.id,
            'vat_number': self.normalize_vat(partner.vat),
            'operation_type': operation_type,
            'register_type': register_type,
            'special_operation': special_operation,
            'key_nif': key_nif,
        }

    def _get_mod140_line_tax(self, tax, move, mod140_line):
        base_move_lines = move.line_ids.filtered(
            lambda l: any(t == tax for t in l.tax_ids))
        base_amount_untaxed = sum(x.credit - x.debit for x in base_move_lines)

        parent_tax = self.env['account.tax'].search([
            ('children_tax_ids.id', '=', tax.id)], limit=1)
        taxes = self.env['account.tax']
        if parent_tax:
            taxes = tax.children_tax_ids
            tax = parent_tax
        else:
            taxes += tax
        fee_move_lines = move.line_ids.filtered(
            lambda l: l.tax_line_id in taxes)
        fee_amount_untaxed = 0.0
        if fee_move_lines:
            fee_amount_untaxed = sum(
                x.credit - x.debit for x in fee_move_lines)

        if mod140_line.line_type in ['received', 'rectification_received']:
            base_amount_untaxed *= -1
            fee_amount_untaxed *= -1

        account_pgc = self.env['account.invoice.line'].search([
            ('invoice_id', '=', mod140_line.invoice_id.id),
            ('invoice_line_tax_ids', 'in', tax.ids)],
            limit=1).account_id.code[:3]

        return {
            'mod140_line_id': mod140_line.id,
            'tax_id': tax.id,
            'base_amount': base_amount_untaxed,
            'tax_amount': fee_amount_untaxed,
            'total_amount': base_amount_untaxed + fee_amount_untaxed,
            'move_line_ids': [(4, aml.id) for aml
                              in base_move_lines + fee_move_lines],
            'account_pgc': account_pgc,
        }

    def _create_mod140_line_tax(self, tax, mod140_line_id, move):
        mod140_line_tax_obj = self.env['l10n.es.bfa.mod140.line.tax']
        vals = self._get_mod140_line_tax(tax, move, mod140_line_id)

        new_record = mod140_line_tax_obj.create(vals)

        return new_record

    def _create_mod140_line(self, move, line_type):
        """
            This function create a new record in issued invoices, Received
            invoices or rectification invoices

            Args:
                move (obj): move

            Returns:
                obj: obj with new object create depends invoice type.
        """
        mod140_line_obj = self.env['l10n.es.bfa.mod140.line']

        vals = self._get_vals_invoice_line(move, line_type)
        exception_text = ""
        exception = False
        if vals['invoice_id'] and not vals['vat_number']:
            exception = True
            exception_text += _("The partner doesn't have a VAT number")

        if exception:
            vals.update({
                'exception': True,
                'exception_text': exception_text,
            })

        return mod140_line_obj.create(vals)

    def _account_move_line_domain(self, taxes):
        # search move lines that contain these tax codes
        return [('date', '>=', self.date_start),
                ('date', '<=', self.date_end),
                '|', ('tax_ids', 'in', taxes.ids),
                ('tax_line_id', 'in', taxes.ids)]

    def _get_account_moves(self, taxes):
        aml_obj = self.env['account.move.line']
        groups = aml_obj.read_group(
            self._account_move_line_domain(taxes), ['move_id'], ['move_id'])
        return self.env['account.move'].browse([
            x['move_id'][0] for x in groups
        ])

    def _create_mod140_records(self, move, line_type, taxes):
        line = self._create_mod140_line(
            move, line_type)
        # Create tax lines filtered by taxes maped
        ml_taxes = move.line_ids.mapped('tax_ids')
        for tax in ml_taxes.filtered(lambda x: x.id in taxes.ids):
            # Create tax lines for the current mod140_line
            self._create_mod140_line_tax(
                tax, line, move)

    # ----------------------------------
    # Account move lines without invoice
    # ----------------------------------
    def _get_account_moves_lines_noinvoice(self):
        aml_obj = self.env['account.move.line']
        lines = aml_obj.search([
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('invoice_id', '=', False),
            ('debit', '!=', 0)])
        # Filter by expenses group PGC account code
        lines_expenses = lines.filtered(
            lambda x: x.account_id.code[:2] in ('62', '64'))

        return lines_expenses

    def _create_mod140_noinvoice_records(self, line):
        """
            This function create a new record in Expense
            without invoice

            Args:
                line (obj): account.move.line
        """

        mod140_line_obj = self.env['l10n.es.bfa.mod140.line.noinvoice']
        """
           Make the dictionary to create a new record in
           Expense without invoice
        """
        vals = {
            'mod140_id': self.id,
            'move_id': line.move_id.id,
            'move_line_id': line.id,
            'ref': line.name,
            'date': line.date,
            'account_pgc': line.account_id.code[:3],
            'amount': line.debit,
        }

        exception_text = ""
        exception = False
        if vals['amount'] < 0:
            exception = True
            exception_text += _("The amount is negative")

        if exception:
            vals.update({
                'exception': True,
                'exception_text': exception_text,
            })

        return mod140_line_obj.create(vals)

    # ----------------------------------
    # Assets in the statement
    # ----------------------------------
    def _get_account_invoice_assets(self):
        aia_obj = self.env['account.invoice']
        invoices = aia_obj.search([
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('type', '=', 'in_invoice'),
            ('use_mod140_asset', '=', True),
            ('mod140_asset_id', '!=', False)])

        # Obtain de Assets used in invoices
        assets = invoices.mapped('mod140_asset_id')

        return assets

    def _create_mod140_asset_statement_records(self, asset):
        """
            This function create a new record in Asset statement

            Args:
                asset: asset_id
        """

        mod140_asset_obj = self.env['l10n.es.bfa.mod140.asset.statement']
        """
           Make the dictionary to create a new record in
           Asset Estatement
        """
        vals = {
            'mod140_id': self.id,
            'asset_id': asset.id,
        }

        exception_text = ""
        exception = False
        # here any logic to evaluate exceptions

        if exception:
            vals.update({
                'exception': True,
                'exception_text': exception_text,
            })

        return mod140_asset_obj.create(vals)

    # ----------------------------------
    # Actions - Buttons
    # ----------------------------------
    @api.multi
    def button_calculate(self):
        self.write({'state': 'calculated',
                    'calculation_date': fields.Datetime.now()})
        """
            Funcion call from mod140
        """
        self._calculate_mod140()
        return True

    @api.multi
    def button_recalculate(self):
        # self.write({'calculation_date': fields.Datetime.now()})
        return self.button_calculate()

    def _clear_old_data(self):
        """
            This function clean all the old data to make a new calculation
        """
        self.line_ids.unlink()
        self.summary_ids.unlink()
        self.tax_summary_ids.unlink()
        self.noinvoice_ids.unlink()
        self.asset_ids.unlink()

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
            # Obtain Map code template from mod140.
            tax_code_map = self.env['l10n.es.aeat.map.tax'].search(
                [('model', '=', '140'),
                 '|',
                 ('date_from', '<=', rec.date_start),
                 ('date_from', '=', False),
                 '|',
                 ('date_to', '>=', rec.date_end),
                 ('date_to', '=', False)], limit=1)
            if not tax_code_map:
                raise UserError(_('No BFA Model 140 Tax Mapping was found'))

            # Obtain all the codes from account.tax.code.template
            codes_issued = tax_code_map.map_line_ids.mapped(
                'tax_ids').filtered(
                lambda t: t.type_tax_use == 'sale').mapped('description')
            codes_received = tax_code_map.map_line_ids.mapped(
                'tax_ids').filtered(
                lambda t: t.type_tax_use == 'purchase').mapped(
                'description')

            # search the account.tax referred to by codes and the company
            taxes_issued = tax_model.search(
                [('description', 'in', codes_issued),
                 ('company_id', 'child_of', rec.company_id.id)])
            taxes_received = tax_model.search(
                [('description', 'in', codes_received),
                 ('company_id', 'child_of', rec.company_id.id)])

            # Get all the account move lines that contain VAT that is
            # applicable to this report.
            # Issued Lines
            moves_issued = rec._get_account_moves(taxes_issued)
            for move in moves_issued:
                line_type = 'issued'
                rec._create_mod140_records(move, line_type, taxes_issued)
            # Received Lines
            moves_received = rec._get_account_moves(taxes_received)
            for move in moves_received:
                line_type = 'received'
                rec._create_mod140_records(move, line_type, taxes_received)


            # Issued Summary
            book_type = 'issued'
            issued_tax_lines = rec.issued_line_ids.mapped(
                'tax_line_ids')
            rectification_issued_tax_lines = \
                rec.rectification_issued_line_ids.mapped(
                    'tax_line_ids')
            tax_summary_data_recs = rec._prepare_mod140_tax_summary(
                issued_tax_lines + rectification_issued_tax_lines, book_type)
            rec._create_mod140_tax_summary(
                tax_summary_data_recs, rec.issued_tax_summary_ids)
            rec._create_mod140_summary(rec.issued_tax_summary_ids, book_type)

            # Received Summary
            book_type = 'received'
            received_tax_lines = rec.received_line_ids.mapped(
                'tax_line_ids')
            rectification_received_tax_lines = \
                rec.rectification_received_line_ids.mapped(
                    'tax_line_ids')
            tax_summary_data_recs = rec._prepare_mod140_tax_summary(
                received_tax_lines + rectification_received_tax_lines,
                book_type)
            rec._create_mod140_tax_summary(
                tax_summary_data_recs, rec.received_tax_summary_ids)
            rec._create_mod140_summary(rec.received_tax_summary_ids,
                                       book_type)

            # Expenses without invoice
            moves_lines_noinvoice = rec._get_account_moves_lines_noinvoice()
            for line in moves_lines_noinvoice:
                rec._create_mod140_noinvoice_records(line)

            # Assets in the statement
            account_invoice_assets = rec._get_account_invoice_assets()
            for asset in account_invoice_assets:
                rec._create_mod140_asset_statement_records(asset)


    @api.multi
    def button_cancel(self):
        """Set report status to cancelled."""
        self.write({'state': 'cancelled'})
        return True

    @api.multi
    def button_recover(self):
        """Set report status to draft and reset calculation date."""
        self.write({'state': 'draft', 'calculation_date': False})
        return True

    @api.multi
    def unlink(self):
        if any(item.state not in ['draft', 'cancelled'] for item in self):
            raise exceptions.UserError(_("Only reports in 'draft' or "
                                       "'cancelled' state can be removed"))
        return super(L10nEsBfaMod140, self).unlink()

    @api.multi
    def view_issued_invoices(self):
        self.ensure_one()
        action = self.env.ref(
            'l10n_es_bfa_mod140.bfa_mod140_issued_html_report_action')
        vals = action.read()[0]
        vals['context'] = self.env.context
        return vals

    @api.multi
    def view_received_invoices(self):
        self.ensure_one()
        action = self.env.ref(
            'l10n_es_bfa_mod140.bfa_mod140_received_html_report_action')
        vals = action.read()[0]
        vals['context'] = self.env.context
        return vals

    @api.model
    def _prepare_bfa_sequence_vals(self, sequence, bfa_num, company):
        return {
            'name': sequence,
            'code': 'bfa.sequence.type',
            'number_increment': 1,
            'implementation': 'no_gap',
            'padding': 7 - len(str(bfa_num)),
            'number_next_actual': 1,
            'prefix': bfa_num,
            'company_id': company.id,
        }

    @api.model_cr
    def _register_hook(self):
        res = super(L10nEsBfaMod140, self)._register_hook()

        bfa_num = getattr(self, '_bfa_number', False)
        if not bfa_num:
            raise exceptions.UserError(_(
                "Modelo no válido: %s. Debe declarar una variable "
                "'_bfa_number'" % self._name
            ))
        seq_obj = self.env['ir.sequence']
        sequence = "bfa%s-sequence" % bfa_num
        companies = self.env['res.company'].search([])
        for company in companies:
            seq = seq_obj.search([
                ('name', '=', sequence), ('company_id', '=', company.id),
            ])
            if seq:
                continue
            seq_obj.create(self.env[self._name]._prepare_bfa_sequence_vals(
                sequence, bfa_num, company,
            ))
        return res

    @api.model
    def _filter_phone(self, phone):
        return (phone or '').replace(" ", "")[-9:]

    @api.model
    def normalize_vat(self, vat):
        # Remove the ES part from spanish vat numbers
        #  (ES12345678Z => 12345678Z)
        vat = re.match("(ES){0,1}(.*)", vat).groups()[1]
        return vat

    @api.model
    def get_html(self):
        """ Render dynamic view from ir.action.client"""
        result = {}
        rcontext = {}
        rec = self.browse(self.env.context.get('active_id'))
        if rec:
            rcontext['o'] = rec
            result['html'] = self.env.ref(self.env.context.get(
                'template_name')).render(
                rcontext)
        return result

    @api.model
    def _get_formatted_date(self, date):
        """Convert an Odoo date to BOE export date format.

        :param date: Date in Odoo format or falsy value
        :return: Date formatted for BOE export.
        """
        if not date:
            return ''
        return datetime.strftime(fields.Date.from_string(date), "%d%m%Y")

    def _format_date(self, date):
        # format date following user language
        lang_model = self.env['res.lang']
        lang = lang_model._lang_get(self.env.user.lang)
        date_format = lang.date_format
        return datetime.strftime(
            fields.Date.from_string(date), date_format)
