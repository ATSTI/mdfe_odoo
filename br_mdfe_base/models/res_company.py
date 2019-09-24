# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    tipo_ambiente_mdfe = fields.Selection(
        [("1", u"Produção"), ("2", u"Homologação")],
        string="Ambiente MDFe",
        default="2",
    )
    tipo_emitente_mdfe = fields.Selection(
        [("1", u"Prestador de Serviço"),
         ("2", u"Transportador de Carga Própria"),
         ('3', u'Prestador de serviço de transporte que emitirá CT-e Globalizado')],
        string="Tipo de Emitente",
        default="2",
    )
