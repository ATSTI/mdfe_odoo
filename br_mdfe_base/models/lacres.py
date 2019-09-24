from odoo import models, fields


class MdfeLacres(models.Model):
    """
    Lacres do MDF-e
    """
    _name = 'mdfe.lacres'

    mdfe = fields.Many2one(
        comodel_name='mdfe.eletronic',
        required=True,
        string=u'MDFe',
        ondelete='cascade'
    )
    numero_lacre = fields.Char(
        size=60,
        string=u'Número do lacre ',
        required=True,
    )


class LacUnidTransp(models.Model):
    """
    Lacres das Unidades de Transporte
    """
    _name = 'lac.unid.transp'

    inf_unid_transp = fields.Many2one(
        comodel_name='inf.unid.transp',
        string=u'Informações das Unidades de Transporte \
        (Carreta/Reboque/Vagão)',
        ondelete='cascade'
    )
    numero_lacre = fields.Char(
        size=20,
        string=u'Número do lacre ',
        required=True,
    )


class LacUnidCarga(models.Model):
    """
    Lacres das Unidades de Carga
    """
    _name = 'lac.unid.carga'

    inf_unid_carga = fields.Many2one(
        comodel_name='inf.unid.carga',
        string=u'Informações das Unidades de Carga \
        (Containeres/ULD/Outros)',
        ondelete='cascade'
    )
    numero_lacre = fields.Char(
        size=20,
        string=u'Número do lacre ',
        required=True,
    )
