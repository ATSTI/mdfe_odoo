import re
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class ModalRodoviario(models.Model):
    _name = 'modal.rodoviario'
    _rec_name = 'veiculos'

    mdfe = fields.Many2one(
        comodel_name='mdfe.eletronic',
        required=True,
        string=u'MDFe',
        ondelete='cascade'
    )
    rntrc = fields.Integer(
        required=False,
        string=u'RNTRC',
        help=u'Registro obrigatório do emitente do MDFe '
             u'junto à ANTT para exercer a atividade '
             u'de transportador rodoviário de cargas por '
             u'conta de terceiros e mediante '
             u'remuneração.'
    )
    ciot = fields.One2many(
        comodel_name='modal.rodoviario.ciot',
        inverse_name='modal_rodoviario',
        required=False,
        string="CIOT",
    )
    condutores = fields.One2many(
        comodel_name='modal.rodoviario.condutores',
        inverse_name='modal_rodoviario',
        required=False,
        string="Condutores",
    )
    veiculos = fields.One2many(
        comodel_name='modal.rodoviario.veiculos',
        inverse_name='modal_rodoviario',
        required=False,
        string="Veiculos",
    )


class ModalRodoviarioCiot(models.Model):
    _name = 'modal.rodoviario.ciot'

    modal_rodoviario = fields.Many2one(
        comodel_name='modal.rodoviario',
        required=True,
        string=u'Informações do modal Rodoviário',
    )
    ciot = fields.Integer(
        required=False,
        string=u'CIOT',
        help=u'Código Identificador da Operação de '
             u'Transporte. Também Conhecido como conta frete'
    )


class ModalRodoviarioCondutores(models.Model):
    _name = 'modal.rodoviario.condutores'

    modal_rodoviario = fields.Many2one(
        comodel_name='modal.rodoviario',
        required=True,
        string=u'Informações do modal Rodoviário',
    )
    condutor = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        string=u'Condutor',
    )
    nome = fields.Char(
        size=60,
        string=u'Nome do condutor',
        required=True,
        compute='coleta_de_dados',
        store=True
    )
    cpf = fields.Char(
        size=11,
        string=u'CPF do Condutor',
        required=True,
        compute='coleta_de_dados',
        store=True
    )

    @api.depends('condutor')
    def coleta_de_dados(self):
        for record in self:
            if len(record.condutor) == 1:
                if record.condutor.cnpj_cpf is not False:
                    if len(re.sub('[^0-9]', '', record.condutor.cnpj_cpf)) == 11:
                        record.cpf = re.sub('[^0-9]', '', record.condutor.cnpj_cpf)
                    else:
                        raise UserError(u'CPF no cadastro, favor inserir')
                else:
                    raise UserError(u'CPF não tem 11 digitos')
                if record.condutor.name is not False:
                    record.nome = record.condutor.name
                else:
                    raise UserError(u'Nome do condutor não informado')


class ModalRodoviarioVeiculos(models.Model):
    _name = 'modal.rodoviario.veiculos'

    modal_rodoviario = fields.Many2one(
        comodel_name='modal.rodoviario',
        required=False,
        string=u'Modal Rodoviario',
    )
    veiculo = fields.Many2one(
        comodel_name='veiculos',
        required=True,
        string=u'Veiculo',
    )
    tipo_veiculo = fields.Selection([
        ('01', u'Reboque'),
        ('02', u'Tração')],
        required=True,
        string=u'Tipo de Veículo'
    )
    codigo_veiculo = fields.Char(
        string=u'Código interno do veículo',
        required=False,
        size=10
    )
    placa = fields.Char(
        string=u'Placa do veículo',
        required=True,
        size=7
    )
    renavam = fields.Char(
        string=u'RENAVAM do veículo ',
        required=False,
        size=11
    )
    tara = fields.Float(
        string=u'Tara em KG',
        required=True,
    )
    cap_kg = fields.Float(
        string=u'Capacidade em KG',
        required=False,
    )
    cap_m3 = fields.Float(
        string=u'Capacidade em M3',
        required=False,
    )
    tipo_rodado = fields.Selection([
        ('01', u'Truck'),
        ('02', u'Toco'),
        ('03', u'Cavalo Mecânico'),
        ('04', u'VAN'),
        ('05', u'Utilitário'),
        ('06', u'Outros')],
        required=True,
        string=u'Tipo de Rodado'
    )
    tipo_carroceria = fields.Selection([
        ('00', u'Não aplicável'),
        ('01', u'Aberta'),
        ('02', u'Fechada/Baú'),
        ('03', u'Granelera'),
        ('04', u'Porta Container'),
        ('05', u'Sider')],
        required=True,
        string=u'Tipo de Carroceria'
    )
    uf = fields.Many2one(
        comodel_name='res.country.state',
        required=True,
        string="UF em que veículo está licenciado",
    )
    proprietario = fields.Many2one(
        comodel_name='modal.rodoviario.veiculos.proprietario',
        required=False,
        string=u'proprietario',
    )

    @api.onchange('veiculo')
    def onchange_veiculo(self):
        if len(self.veiculo) == 1:
            self.tipo_veiculo = self.veiculo.tipo_veiculo
            self.codigo_veiculo = self.veiculo.codigo_veiculo
            self.placa = self.veiculo.placa
            self.placa = self.veiculo.placa
            self.renavam = self.veiculo.renavam
            self.tara = self.veiculo.tara
            self.cap_kg = self.veiculo.cap_kg
            self.cap_m3 = self.veiculo.cap_m3
            self.tipo_rodado = self.veiculo.tipo_rodado
            self.tipo_carroceria = self.veiculo.tipo_carroceria
            if len(self.veiculo.uf) == 1:
                self.uf = self.veiculo.uf.id
            if len(self.veiculo.proprietario) == 1:
                self.proprietario = self.veiculo.proprietario.id


class ModalRodoviarioVeiculosProprietario(models.Model):
    _name = 'modal.rodoviario.veiculos.proprietario'

    veiculos = fields.One2many(
        comodel_name='modal.rodoviario.veiculos',
        inverse_name='proprietario',
        required=True,
        string="UF do proprietário",
    )
    proprietario = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        string=u'Proprietario',
    )
    cnpj_cpf = fields.Char(
        size=14,
        string=u'CNPJ ou CPF do proprietário',
        required=True,
        compute='coleta_de_dados',
        store=True
    )
    rntrc = fields.Integer(
        required=True,
        string=u'RNTRC do proprietário',
        help=u'Registro obrigatório do emitente do MDFe '
             u'junto à ANTT para exercer a atividade '
             u'de transportador rodoviário de cargas por '
             u'conta de terceiros e mediante '
             u'remuneração.'
    )
    nome = fields.Char(
        size=60,
        string=u'Razão Social ou Nome do proprietário',
        required=True,
        compute='coleta_de_dados',
        store=True
    )
    ie = fields.Char(
        size=60,
        string=u'Inscrição Estadual do proprietário',
        required=True,
        compute='coleta_de_dados',
        store=True
    )
    uf = fields.Many2one(
        comodel_name='res.country.state',
        required=True,
        string=u'UF do proprietário',
        compute='coleta_de_dados',
        store=True
    )
    tipo_prop = fields.Selection([
        ('0', u'TAC – Agregado'),
        ('1', u'TAC Independente'),
        ('2', u'Outros')],
        required=True,
        string=u'Tipo Proprietário'
    )

    @api.depends('proprietario')
    def coleta_de_dados(self):
        for record in self:
            if len(record.proprietario) == 1:
                erros = []
                if record.proprietario.name is False:
                    erros.append(u'Nome do proprietario '
                                 u'inválido ou não foi informado\n ')

                if record.proprietario.cnpj_cpf is False:
                    erros.append(u'CNPJ ou CPF do proprietario '
                                 u'inválido ou não foi informado\n ')

                if len(record.proprietario.state_id) == 0:
                    erros.append(u'Estado do proprietario inválido '
                                 u'ou não foi informado\n ')

                if len(erros) > 0:
                    raise UserError(erros)

                record.nome = record.proprietario.name
                record.cnpj_cpf = re.sub('[^0-9]', '', record.proprietario.cnpj_cpf)
                record.ie = re.sub('[^0-9]', '', record.proprietario.inscr_est)
                record.uf = record.proprietario.state_id


class Veiculos(models.Model):
    _name = 'veiculos'
    _rec_name = 'placa'

    tipo_veiculo = fields.Selection([
        ('01', u'Reboque'),
        ('02', u'Tração')],
        required=True,
        string=u'Tipo de Veículo'
    )
    codigo_veiculo = fields.Char(
        string=u'Código interno do veículo',
        required=False,
        size=10
    )
    placa = fields.Char(
        string=u'Placa do veículo',
        required=True,
        size=7
    )
    renavam = fields.Char(
        string=u'RENAVAM do veículo ',
        required=False,
        size=11
    )
    tara = fields.Float(
        string=u'Tara em KG',
        required=True,
    )
    cap_kg = fields.Float(
        string=u'Capacidade em KG',
        required=False,
    )
    cap_m3 = fields.Float(
        string=u'Capacidade em M3',
        required=False,
    )
    tipo_rodado = fields.Selection([
        ('01', u'Truck'),
        ('02', u'Toco'),
        ('03', u'Cavalo Mecânico'),
        ('04', u'VAN'),
        ('05', u'Utilitário'),
        ('06', u'Outros')],
        required=True,
        string=u'Tipo de Rodado'
    )
    tipo_carroceria = fields.Selection([
        ('00', u'Não aplicável'),
        ('01', u'Aberta'),
        ('02', u'Fechada/Baú'),
        ('03', u'Granelera'),
        ('04', u'Porta Container'),
        ('05', u'Sider')],
        required=True,
        string=u'Tipo de Carroceria'
    )
    uf = fields.Many2one(
        comodel_name='res.country.state',
        required=True,
        string="UF em que veículo está licenciado",
    )
    proprietario = fields.Many2one(
        comodel_name='veiculos.proprietario',
        required=False,
        string=u'proprietario',
    )

    @api.model
    def create(self, vals):
        vals['codigo_veiculo'] = self.env['ir.sequence'].\
            next_by_code('mdfe_eletronic_code_veiculo')

        return super(Veiculos, self).create(vals)


class VeiculosProprietario(models.Model):
    _name = 'veiculos.proprietario'
    _rec_name = 'proprietario'

    veiculos = fields.One2many(
        comodel_name='veiculos',
        inverse_name='proprietario',
        required=True,
        string="UF do proprietário",
    )
    proprietario = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        string=u'Proprietario',
    )
    cnpj_cpf = fields.Char(
        size=14,
        string=u'CNPJ ou CPF do proprietário',
        required=True,
        compute='coleta_de_dados',
        store=True
    )
    rntrc = fields.Integer(
        required=True,
        string=u'RNTRC do proprietário',
        help=u'Registro obrigatório do emitente do MDFe '
             u'junto à ANTT para exercer a atividade '
             u'de transportador rodoviário de cargas por '
             u'conta de terceiros e mediante '
             u'remuneração.'
    )
    nome = fields.Char(
        size=60,
        string=u'Razão Social ou Nome do proprietário',
        required=True,
        compute='coleta_de_dados',
        store=True
    )
    ie = fields.Char(
        size=60,
        string=u'Inscrição Estadual do proprietário',
        required=True,
        compute='coleta_de_dados',
        store=True
    )
    uf = fields.Many2one(
        comodel_name='res.country.state',
        required=True,
        string=u'UF do proprietário',
        compute='coleta_de_dados',
        store=True
    )
    tipo_prop = fields.Selection([
        ('0', u'TAC – Agregado'),
        ('1', u'TAC Independente'),
        ('2', u'Outros')],
        required=True,
        string=u'Tipo Proprietário'
    )

    @api.depends('proprietario')
    def coleta_de_dados(self):
        for record in self:
            if len(record.proprietario) == 1:
                erros = []
                if record.proprietario.name is False:
                    erros.append(u'Nome do proprietario '
                                 u'inválido ou não foi informado\n ')

                if record.proprietario.cnpj_cpf is False:
                    erros.append(u'CNPJ ou CPF do proprietario '
                                 u'inválido ou não foi informado\n ')

                if len(record.proprietario.state_id) == 0:
                    erros.append(u'Estado do proprietario inválido '
                                 u'ou não foi informado\n ')

                if len(erros) > 0:
                    raise UserError(erros)

                record.nome = record.proprietario.name
                record.cnpj_cpf = re.sub('[^0-9]', '', record.proprietario.cnpj_cpf)
                record.ie = re.sub('[^0-9]', '', record.proprietario.inscr_est)
                record.uf = record.proprietario.state_id
