# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Adaptaciones plan contable e impuestos para la BFA',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'author': 'Jesus Ramiro (Bilbonet.NET)',
    'website': 'https://www.bilbonet.net',
    'depends': [
        'l10n_es',
    ],
    'data': [
        'data/account_tax_data.xml',
        'data/sequence_data.xml',
        'data/account_journal_data.xml',
    ],
    'installable': True,
}
