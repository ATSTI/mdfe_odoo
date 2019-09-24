from odoo import models, fields


class InfMunDesca(models.Model):

    _name = 'inf.mun.desca'

    mdfe = fields.Many2one(
        comodel_name='mdfe.eletronic',
        required=True,
        string=u'MDFe',
        ondelete='cascade'
    )
    mun = fields.Many2one(
        comodel_name='res.state.city',
        required=True,
        string=u"Município",
    )
    inf_documents = fields.One2many(
        comodel_name="inf.documents",
        inverse_name="inf_mun_desca",
        required=True
    )
