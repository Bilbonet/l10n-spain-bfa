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
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/bfa_mod140_view.xml',
    ],
    'installable': True,
}
