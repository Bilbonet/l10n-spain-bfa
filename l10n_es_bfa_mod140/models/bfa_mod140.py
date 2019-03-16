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
        string="Surnames, Name", size=40,
        help="Declarant full name, must have surnames, name.",
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    declarant_phone = fields.Char(
        string="Phone", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    declarant_mobile = fields.Char(
        string="Mobile", size=9, required=True, readonly=True,
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
        string="Surnames, Name", size=40,
        help="Contact full name, must have surnames, name.",
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    contact_phone = fields.Char(
        string="Phone", size=9, required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    contact_mobile = fields.Char(
        string="Mobile", size=9, required=True, readonly=True,
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

        #Declarant Data
        self.declarant_name = self.env.user.partner_id.lastname + ', ' + \
                              self.env.user.partner_id.firstname
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
        self.contact_name = self.env.user.partner_id.lastname + ', ' + \
                            self.env.user.partner_id.firstname
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

    @api.onchange('representative_vat')
    def onchange_representative_vat(self):
        if self.company_vat == self.representative_vat:
            raise exceptions.UserError(_(
                "Company vat and representative vat can't be equals."
            ))

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
        self.write({'calculation_date': fields.Datetime.now()})
        return self.button_calculate()

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
        return {
            'line_type': line_type,
            'invoice_date': move.date,
            'partner_id': partner.id,
            'vat_number': partner.vat,
            'invoice_id': invoice.id,
            'ref': ref,
            'external_ref': ext_ref,
            'mod140_id': self.id,
            'move_id': move.id,
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

        if mod140_line.line_type == 'issued' and fee_amount_untaxed < 0.0:
            mod140_line.line_type = 'rectification_issued'

        if mod140_line.line_type == 'received' and fee_amount_untaxed > 0.0:
            mod140_line.line_type = 'rectification_received'

        if mod140_line.line_type in ['received', 'rectification_received']:
            base_amount_untaxed *= -1
            fee_amount_untaxed *= -1

        # Busca la C.C en la linea de la factura que contenga el impuesto
        account_pgc = self.env['account.invoice.line'].search([
            ('invoice_id', '=', fee_move_lines.invoice_id.id),
            ('invoice_line_tax_ids', 'in', tax.id)],
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
        # Create tax lines
        ml_taxes = move.line_ids.mapped('tax_ids')
        for tax in ml_taxes.filtered(lambda x: x.id in taxes.ids):
            # Create tax lines for the current mod140_line
            self._create_mod140_line_tax(
                tax, line, move)

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

            # Obtain all the codes from account.tax
            codes_issued = self.env['account.tax'].search(
                [('type_tax_use', '=', 'sale'),
                 ('amount', '>=', '0')]).mapped('description')
            codes_received = self.env['account.tax'].search(
                [('type_tax_use', '=', 'purchase'),
                 ('amount', '>=', '0')]).mapped('description')

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
    def _filter_phone(self, phone):
        return (phone or '').replace(" ", "")[-9:]

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