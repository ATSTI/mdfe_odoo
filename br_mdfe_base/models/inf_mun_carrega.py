from odoo import api, models, fields


class InfMunCarrega(models.Model):
    _name = 'inf.mun.carrega'

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

