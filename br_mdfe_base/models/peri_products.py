from odoo import api, models, fields
from odoo.addons import decimal_precision as dp


class PeriProducts(models.Model):
    _name = 'peri.products'

    inf_documents = fields.Many2one(
        comodel_name='inf.documents',
        required=True,
        string=u'Documentos',
        ondelete='cascade'
    )
    n_onu = fields.Char(
        string=u'Número ONU/UN',
        required=True,
        size=4,
        help='informar o número ONU/UN. Ver a legislação de transporte de'
             ' produtos perigosos aplicadas ao modal.'
    )
    xnome_ae = fields.Char(
        string=u'Nome para embarque do produto',
        required=False,
        size=150,
        help='informar o nome apropriado para embarque do produto. '
             'Ver a legislação de transporte de produtos perigosos '
             'aplicadas ao modal.'
    )
    xcla_risco = fields.Char(
        string=u'Informar a classe',
        required=False,
        size=150,
        help='informar a classe ou subclasse/divisão, e '
             'risco subsidiário/risco secundário.'
    )
    gr_emb = fields.Char(
        string=u'Informar o grupo de embalagem',
        required=False,
        size=6
    )
    q_tot_prod = fields.Float(
        string=u'Informar a quantidade total do produto',
        required=True,
        digits=dp.get_precision('Account')
    )
    q_vol_tipo = fields.Char(
        size=60,
        required=False,
        string=u'Informar a quantidade e tipo de volumes',
    )
