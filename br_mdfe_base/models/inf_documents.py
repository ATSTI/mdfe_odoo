from odoo import api, models, fields


class InfDocuments(models.Model):

    _name = 'inf.documents'

    inf_mun_desca = fields.Many2one(
        comodel_name='inf.mun.desca',
        required=True,
        string=u'Informações dos Municípios de descarregamento',
        ondelete='cascade'
    )
    tp_document = fields.Selection([
        ('1', u'CTe - Conhecimentos de Tranporte - Eletronico'),
        ('2', u'NFe - Nota Fiscal Eletronica'),
        ('3', u'MDFe - Manifesto Eletrônico de Documentos Fiscais')],
        string=u'Tipo de Documento',
        required=True,
    )
    ind_reentrega = fields.Boolean(
        required=False,
        string=u'Indicador de Reentrega',
        help=u'Esse campo é usado quando a primeira '
             u'entrega falhou por algum motivo'
    )
    inf_unid_transp = fields.One2many(
        comodel_name='inf.unid.transp',
        inverse_name="inf_documents",
        required=False,
        string=u'Informações das Unidades de Transporte',
        help='Deve ser preenchido com as informações \
        das unidades de transporte utilizadas.'
    )
    chave = fields.Char(
        string=u'Chave',
        size=44,
        required=True,
    )
    seg_cod_barra = fields.Char(
        string=u'Segundo código de barras',
        size=36,
        required=False,
    )

