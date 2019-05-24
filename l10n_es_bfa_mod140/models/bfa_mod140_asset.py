# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class L10nEsBfaMod140Asset(models.Model):
    _name = "l10n.es.bfa.mod140.asset"
    _description = "BFA Modelo 140 Accounting Assets"

    company_id = fields.Many2one(
        comodel_name='res.company', string="Company", required=True,
        readonly=True,
        default=lambda self: self.env['res.company']._company_default_get())
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
        " the asset without removing it.")
    ref = fields.Char(string="Asset Reference", size=10, required=True)
    name = fields.Char(string="Asset Description", size=50, required=True)
    type_operation = fields.Selection(
        selection=[
            ('A', 'Alta'),
            ('B', 'Baja'),
            ('C', 'Mejora'),
            ('D', 'Regularización'),
        ],
        string='Type of operation', default='A', required=True)
    date_operation = fields.Date(string="Operation date", required=True)
    date_start = fields.Date(string="Starting date", required=True)
    titularity = fields.Selection(
        selection=[
            ('P', 'Propiedad'),
            ('A', 'Alquiler'),
            ('F', 'Arrendamiento Financiero'),
            ('O', 'Otros'),
        ],
        string='Titularity of the asset', default='P', required=True)
    type_asset = fields.Selection(
        selection=[
            ('A', 'Local'),
            ('B', 'Otros inmuebles'),
            ('C', 'Medios de transporte'),
            ('D', 'Teléfono fijo'),
            ('E', 'Teléfono móvil'),
            ('F', 'Fax'),
            ('G', 'Mobiliario'),
            ('H', 'Maquinaria'),
            ('I', 'Equipo Informático'),
            ('J', 'Instalaciones'),
            ('K', 'Bienes grupo 20 PGC'),
            ('L', 'Otros bienes grupo 21 PGC'),
            ('M', 'Bienes grupo 23 PGC'),
            ('N', 'Solar'),
        ],
        string='Type of asset', default='A', required=True)
    account_pgc = fields.Integer(string='Account in the PGC',
                                 size=3, required=True)

    _sql_constraints = [
        ('ref_uniq', 'unique(ref)',
         _('Asset reference must be unique!'))
    ]
