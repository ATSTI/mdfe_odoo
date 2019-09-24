from odoo import models, fields


class InfUnidTransp(models.Model):
    """
    Informações das Unidades de Transporte
    (Carreta/Reboque/Vagão)

    Deve ser preenchido com as informações
    das unidades de transporte utilizadas.
    """
    _name = 'inf.unid.transp'

    inf_documents = fields.Many2one(
        comodel_name='inf.documents',
        required=True,
        string=u'Documentos',
        ondelete='cascade'
    )
    inf_unid_carga = fields.One2many(
        comodel_name='inf.unid.carga',
        inverse_name="inf_unid_transp",
        required=False,
        string=u'Informações das Unidades de Carga \
            (Containeres/ULD/Outros)',
        help='Dispositivo de carga utilizada (Unit Load \
            Device - ULD) significa todo tipo de \
            contêiner de carga, vagão, contêiner de \
            avião, palete de aeronave com rede ou \
            palete de aeronave com rede sobre um \
            iglu.'
    )
    tp_unid_transp = fields.Selection([
        ('1', u'Rodoviário Tração'),
        ('2', u'Rodoviário Reboque'),
        ('3', u'Navio'),
        ('4', u'Balsa'),
        ('5', u'Aeronave'),
        ('6', u'Vagão'),
        ('7', u'Outros')],
        string=u'Tipo da Unidade de Transporte',
        required=True,
    )
    id_unid_transp = fields.Char(
        string=u'Identificação da Unidade de Transporte',
        size=20,
        required=False,
        help='Informar a identificação conforme o tipo \
        de unidade de transporte.<br />\
        Por exemplo: para rodoviário tração ou\
        reboque deverá preencher com a placa\
        do veículo. '
    )
    lac_unid_transp = fields.One2many(
        comodel_name='lac.unid.transp',
        inverse_name="inf_unid_transp",
        required=False,
        string=u'Lacres',
    )
    qtd_rat = fields.Float(
        string=u'Quantidade rateada (Peso,Volume) ',
        required=False,
    )


class InfUnidCarga(models.Model):
    """
    Informações das Unidades de Carga (Containeres/ULD/Outros)

    Dispositivo de carga utilizada (Unit Load
    Device - ULD) significa todo tipo de
    contêiner de carga, vagão, contêiner de
    avião, palete de aeronave com rede ou
    palete de aeronave com rede sobre um
    iglu.
    """
    _name = 'inf.unid.carga'

    inf_unid_transp = fields.Many2one(
        comodel_name='inf.unid.transp',
        required=True,
        string=u'Unidades de transporte',
        ondelete='cascade'
    )
    tp_unid_carga = fields.Selection([
        ('1', u'Container'),
        ('2', u'ULD'),
        ('3', u'Pallet'),
        ('4', u'Outros')],
        string=u'Tipo da Unidade de Carga',
        required=True,
    )
    id_unid_carga = fields.Char(
        string=u'Identificação da Unidade de Carga',
        size=20,
        required=False,
        help='Informar a identificação da unidade de \
        carga, por exemplo: número do container.'
    )
    lac_unid_carga = fields.One2many(
        comodel_name='lac.unid.carga',
        inverse_name="inf_unid_carga",
        required=False,
        string=u'Lacres',
    )
    qtd_rat = fields.Float(
        string=u'Quantidade rateada (Peso,Volume) ',
        required=False,
    )
