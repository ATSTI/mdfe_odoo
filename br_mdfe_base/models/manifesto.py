# coding=utf-8
import re
import sys
import random
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
from mdfelib.v3_00 import mdfe as mdfe3
from mdfelib.v3_00 import mdfeModalRodoviario as rodo3
from odoo.addons import decimal_precision as dp


_logger = logging.getLogger(__name__)


class MdfeEletronic(models.Model):
    _name = 'mdfe.eletronic'

    emitente = fields.Many2one(
        comodel_name='res.company',
        required=True,
        string=u'Emitente da MDF-e',
        default=lambda self: self.env.user.company_id
    )
    emit_nome = fields.Char(
        size=60,
        string=u'Razão social ou Nome do emitente',
    )
    emit_fantasia = fields.Char(
        size=60,
        string=u'Nome fantasia do emitente',
    )
    emit_inscr_est = fields.Char(
        string=u'Inscr. Estadual/RG',
        size=16,
    )
    emit_cnpj_cpf = fields.Char(
        size=14,
        string=u'CNPJ ou CPF do Parceiro',
    )
    emit_logradouro = fields.Char(
        string=u'Logradouro',
    )
    emit_nro = fields.Char(
        size=10,
        string=u'Número',
    )
    emit_xcpl = fields.Char(
        string=u'Complemento',
    )
    emit_bairro = fields.Char(
        string=u'Bairro',
    )
    emit_mun = fields.Many2one(
        comodel_name='res.state.city',
        string=u"Município",
    )
    emit_uf = fields.Many2one(
        comodel_name='res.country.state',
        string=u"Estado",
    )
    emit_cep = fields.Char(
        string=u'CEP',
    )
    emit_fone = fields.Char(
        string=u'Telefone',
    )
    emit_email = fields.Char(
        string=u'E-mail'
    )
    amb = fields.Selection([
        ('1', u'Produção'),
        ('2', u'Homologação')],
        string=u'Ambiente',
        required=True
    )
    tipo_emitente_mdfe = fields.Selection([
        ('1', u'Prestador de serviço de transporte'),
        ('2', u'Transportador de Carga Própria'),
        ('3', u'Prestador de serviço de transporte que emitirá CT-e '
              u'Globalizado')],
        required=True,
        string=u'Tipo de Emitente',
    )
    tipo_tranpor = fields.Selection([
        ('1', u'ETC'),
        ('2', u'TAC'),
        ('3', u'CTC')],
        required=False,
        string=u'Tipo do Transportador',
    )
    ind_canal_verde = fields.Boolean(
        required=False,
        string='Canal Verde',
        help=u'Participante do projeto Canal Verde'
    )
    serie = fields.Many2one(
        string=u'Série',
        comodel_name='br_account.document.serie'
    )
    numero_mdfe = fields.Char(
        string=u'Número',
        readonly=True
    )
    chave = fields.Char(
        string=u'Chave de Acesso',
        readonly=True
    )
    codigo_mdfe = fields.Integer()
    cdv = fields.Integer()
    modal = fields.Selection([
        ('1', u'Rodoviário'),
        ('2', u'Aéreo'),
        ('3', u'Aquaviário'),
        ('4', u'Ferroviário')],
        required=True,
        string=u'Modalidade de transporte'
    )
    data_emissao = fields.Datetime(
        string=u'Data emissão',
        readonly=True
    )
    dh_ini_viagem = fields.Datetime(
        string=u'Data e hora previstos de início da viagem',
        required=False
    )
    inf_mun_carrega = fields.One2many(
        comodel_name='inf.mun.carrega',
        inverse_name='mdfe',
        string="Informações dos Municípios de carregamento",
    )
    inf_percurso = fields.One2many(
        comodel_name='inf.percurso',
        inverse_name='mdfe',
        string="Informações do Percurso do MDF-e",
    )
    inf_mun_descarga = fields.One2many(
        comodel_name='inf.mun.desca',
        inverse_name='mdfe',
        string="Informações dos Municípios de descarregamento",
    )
    valor_carga = fields.Float(
        string=u'Valor total da carga / mercadorias transportadas',
        digits=dp.get_precision('Account')
    )
    codigo_unid = fields.Selection([
        ('1', u'KG'),
        ('2', u'TON')],
        required=True,
        string=u'Unidade de medida',
        help=u'Unidade de medida do Peso '
        u'Bruto da Carga / Mercadorias transportadas'
    )
    qtd_carga = fields.Float(
        string=u'Peso Bruto',
        help=u'Total da Carga / Mercadorias transportadas',
        digits=dp.get_precision('Account')
    )
    lacres = fields.One2many(
        comodel_name='mdfe.lacres',
        inverse_name='mdfe',
        string="Lacres do MDF-e",
    )
    aut_xml = fields.One2many(
        comodel_name='aut.xml',
        inverse_name='mdfe',
        string=u"Autorizados para download do XML do DF-e",
    )
    inf_ad_fisco = fields.Text(
        string=u'Informações adicionais de interesse do Fisco'
    )
    inf_cpl = fields.Text(
        string=u'Informações complementares de interesse do Contribuinte'
    )

    @api.onchange('emitente')
    def dados_emitente_onchange(self):
        if len(self.emitente) == 1:
            erros = []
            partner_id = self.emitente.partner_id
            serie = self.env['br_account.document.serie'].search([
                ['company_id', '=', self.emitente.id],
                ['active', '=', True],
            ])
            if len(serie) == 0:
                self.serie = serie.id

            if partner_id.name is False:
                erros.append(u'Nome do emitente '
                             u'inválido ou não foi informado\n ')

            if partner_id.cnpj_cpf is False:
                erros.append(u'CNPJ ou CPF do emitente '
                             u'inválido ou não foi informado\n ')

            if partner_id.street is False:
                erros.append(u'Logradouro do emitente '
                             u'inválido ou não foi informado\n ')

            if partner_id.number is False:
                erros.append(u'Número do endereço do emitente '
                             u'inválido ou não foi informado\n ')

            if partner_id.district is False:
                erros.append(u'Bairro do emitente inválido '
                             u'ou não foi informado\n ')

            if len(partner_id.city_id) == 0:
                erros.append(u'Cidade do emitente inválido '
                             u'ou não foi informado\n ')

            if len(partner_id.state_id) == 0:
                erros.append(u'Estado do emitente inválido '
                             u'ou não foi informado\n ')

            if partner_id.zip is False:
                erros.append(u'Cep do emitente inválido '
                             u'ou não foi informado\n ')

            if self.emitente.tipo_ambiente_mdfe is False:
                erros.append(u'Ambiente Homologação ou Produção do emitente '
                             u'não foi informado\n ')

            if len(erros) > 0:
                raise UserError(erros)

            self.emit_nome = partner_id.legal_name
            self.emit_fantasia = partner_id.name
            self.emit_cnpj_cpf = \
                re.sub('[^0-9]', '', partner_id.cnpj_cpf)
            self.emit_inscr_est = \
                re.sub('[^0-9]', '', partner_id.inscr_est)
            self.emit_logradouro = partner_id.street
            self.emit_nro = partner_id.number
            self.emit_xcpl = partner_id.street2
            self.emit_bairro = partner_id.district
            self.emit_mun = partner_id.city_id
            self.emit_uf = partner_id.state_id
            self.emit_cep = partner_id.zip
            self.emit_fone = partner_id.phone
            self.emit_email = partner_id.email
            self.amb = self.emitente.tipo_ambiente_mdfe

    @api.model
    def create(self, vals):
        if 'inf_mun_carrega' not in vals or len(vals['inf_mun_carrega']) == 0:
            raise UserError(u'Você precisa pelo menos ter '
                            u'1 Município de carregamento')

        if len(vals['inf_mun_carrega']) > 50:
            raise UserError(u'Você só pode ter no máximo'
                            u'50 Município de carregamento')

        # Validação dos municípios para que todos tenha a mesma UF
        mun_ini = self.env['res.state.city']. \
            search([('id', '=', vals['inf_mun_carrega'][0][2]['mun'])])
        mun_ini = mun_ini.state_id.code
        for carregamento in vals['inf_mun_carrega']:
            mun = self.env['res.state.city'].\
                search([('id', '=', carregamento[2]['mun'])])

            if mun_ini != mun.state_id.code:
                raise UserError(u'Os municípios de carregamento '
                                u'devem pertencer a mesma UF')

            # Validação dos municípios para que não haja repetidos
            count = 0
            for carregamento1 in vals['inf_mun_carrega']:
                if carregamento[2]['mun'] == carregamento1[2]['mun']:
                    count += 1
                if count > 1:
                    raise UserError(
                        u'Existe municípios de carregamento repetidos')

        if 'inf_percurso' in vals and len(vals['inf_percurso']) > 25:
            raise UserError(u'Você só pode ter no máximo'
                            u'50 Unidades Federativas de Percurso')

        if 'inf_mun_descarga' not in vals or \
                len(vals['inf_mun_descarga']) == 0:
            raise UserError(u'Você precisa pelo menos ter '
                            u'1 Município de descarregamento')

        if len(vals['inf_mun_descarga']) > 100:
            raise UserError(u'Você só pode ter no máximo'
                            u'100 Município de descarregamento')

        # Validação dos municípios para que todos tenha a mesma UF
        mun_fim = self.env['res.state.city']. \
            search([('id', '=', vals['inf_mun_descarga'][0][2]['mun'])])
        mun_fim = mun_fim.state_id.code
        for descarregamento in vals['inf_mun_descarga']:
            mun = self.env['res.state.city'].\
                search([('id', '=', descarregamento[2]['mun'])])

            if mun_fim != mun.state_id.code:
                raise UserError(u'Os municípios de descarregamento '
                                u'devem pertencer a mesma UF')

            # Validação dos municípios para que não haja repetidos
            count = 0
            for descarregamento1 in vals['inf_mun_descarga']:
                if descarregamento[2]['mun'] == descarregamento1[2]['mun']:
                    count += 1
                if count > 1:
                    raise UserError(
                        u'Existe municípios de descarregamento repetidos')

        vals['numero_mdfe'] = self.env['ir.sequence'].\
            next_by_code('mdfe_eletronic_numero')

        vals['codigo_mdfe'] = random.randrange(0, 99999999, 8)
        return super(MdfeEletronic, self).create(vals)

    @api.multi
    def validar_mdfe(self):
        vals = self._prepare_edoc_modal()
        ender_emit = mdfe3.TEndeEmi(
            xLgr=str(self.emit_logradouro),
            nro=str(self.emit_nro),
            xBairro=str(self.emit_bairro),
            cMun='%s%s' % (
                self.emit_uf.ibge_code,
                self.emit_mun.ibge_code),
            xMun=str(self.emit_mun.name),
            CEP=re.sub('[^0-9]', '', str(self.emit_cep)),
            UF=str(self.emit_uf.code)
        )
        emit = mdfe3.emitType(
            CNPJ=self.emit_cnpj_cpf,
            IE=self.emit_inscr_est,
            xNome=self.emit_nome,
            xFant=self.emit_fantasia,
            enderEmit=ender_emit
        )

        carregamentos = []
        for carregamento in self.inf_mun_carrega:
            carregamento_append = mdfe3.infMunCarregaType(
                cMunCarrega='%s%s' % (
                    carregamento.mun.state_id.ibge_code,
                    carregamento.mun.ibge_code
                ),
                xMunCarrega=carregamento.mun.ibge_code.name
            )
            carregamentos.append(carregamento_append)

        ide = mdfe3.ideType(
            cUF=str(self.emit_uf.ibge_code),
            tpAmb=self.amb,
            tpEmit=self.tipo_emit,
            tpTransp=None if self.tipo_tranpor is False else '1',
            mod=58,
            serie=self.serie,
            nMDF=self.numero_mdfe,
            cMDF=self.codigo_mdfe,
            cDV=self.cdv,
            modal=self.modal,
            dhEmi=self.data_emissao,
            tpEmis=1,
            procEmi='0',
            verProc='Odoo',
            UFIni=self.inf_mun_carrega[0].code,
            UFFim=self.inf_mun_descarga[0].code,
            infMunCarrega=carregamentos,
            infPercurso=None,
            dhIniViagem=None,
            indCanalVerde=None,
        )

    def _prepare_edoc_modal(self):
        # Validação e preparativo do modal
        vals = {}
        if self.emit_fone is not False:
            vals['enderEmit']['fone'] = self.emit_fone
        return vals
