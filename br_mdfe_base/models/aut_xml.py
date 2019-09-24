from odoo import api, models, fields
import re
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AutXml(models.Model):
    _name = 'aut.xml'

    mdfe = fields.Many2one(
        comodel_name='mdfe.eletronic',
        required=True,
        string=u'MDFe',
        ondelete='cascade'
    )
    parceiro = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        string=u"Parceiro",
    )
    cnpj_cpf = fields.Char(
        size=14,
        string=u'CNPJ ou CPF do Parceiro',
        required=True,
        compute='coleta_de_cnpj',
        store=True
    )

    @api.depends('parceiro')
    def coleta_de_cnpj(self):
        for record in self:
            if len(record.parceiro) == 1:
                if record.parceiro.cnpj_cpf is not False:
                    record.cnpj_cpf = re.sub('[^0-9]', '', record.parceiro.cnpj_cpf)
                else:
                    raise UserError(
                        u'O parceiro não possui um CNPJ ou '
                        u'CPF no cadastro, favor inserir'
                    )
