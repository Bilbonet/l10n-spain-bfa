# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'BFA Modelo 140',
    'version': '11.0.1.0.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'author': 'Jesus Ramiro (Bilbonet.NET)',
    'website': 'https://www.bilbonet.net',
    'depends': [
        'l10n_es',
        'base_vat',
        'l10n_es_aeat',
        'l10n_es_bfa',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/map_taxes_mod140.xml',
        'data/bfa_export_mod140_activity_data.xml',
        'data/bfa_export_mod140_incomes_data.xml',
        'data/bfa_export_mod140_expenses_data.xml',
        'data/bfa_export_mod140_expenses_noinvoice_data.xml',
        'data/bfa_export_mod140_data.xml',
        'wizard/mod140_export_to_bob_wizard.xml',
        'views/bfa_mod140_view.xml',
        'views/bfa_mod140_line_view.xml',
        'views/bfa_mod140_summary_view.xml',
        'views/bfa_mod140_tax_summary_view.xml',
        'views/bfa_mod140_line_noinvoice_view.xml',
        'views/bfa_mod140_asset_view.xml',
        'report/common_templates.xml',
        'report/bfa_mod140_report.xml',
        'report/bfa_mod140_invoices_issued_report.xml',
        'report/bfa_mod140_invoices_received_report.xml',
    ],
    'installable': True,
}
