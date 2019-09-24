from odoo import api, models, fields


class InfPercurso(models.Model):
    _name = 'inf.percurso'

    mdfe = fields.Many2one(
        comodel_name='mdfe.eletronic',
        required=True,
        string=u'MDFe',
        ondelete='cascade'
    )
    uf = fields.Many2one(
        comodel_name='res.country.state',
        required=True,
        string=u"Município",
    )
