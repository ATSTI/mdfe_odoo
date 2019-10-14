from odoo import api, models, fields
from odoo.addons import decimal_precision as dp


class InfEntregaParcial(models.Model):
    _name = 'inf.entrega.parcial'

    inf_documents = fields.Many2one(
        comodel_name='inf.documents',
        required=True,
        string=u'Documentos',
        ondelete='cascade'
    )
    qtd_total = fields.Float(
        string=u'informar a quantidade total de volumes',
        digits=dp.get_precision('Account'),
        required=True
    )
    qtd_parcial = fields.Float(
        string=u'informar a quantidade parcial de volumes',
        digits=dp.get_precision('Account'),
        required=True
    )
