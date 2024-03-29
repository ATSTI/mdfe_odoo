# coding=utf-8
import re
import random
import logging
import sys
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from datetime import datetime
from pytz import timezone
from .mdfe_v3_00 import *

_logger = logging.getLogger(__name__)


class MdfeEletronic(models.Model):
    _name = 'mdfe.eletronic'

    name = fields.Char()
    state = fields.Selection([
        ('done', u'Autorizado o uso do MDF-e'),
        ('canceled', u'Cancelamento de MDF-e homologado'),
        ('received', u'Arquivo recebido com sucesso'),
        ('processed', u'Arquivo processado'),
        ('processing', u'Arquivo em processamento'),
        ('closed', u'Encerramento de MDF-e homologado'),
        ('rejected', u'Rejeitado')],
        required=True,
        string=u'Situação'
    )
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
        ('2', u'Transportador de Carga Própria')],
        required=True,
        string=u'Tipo de Emitente',
    )
    tipo_emissao = fields.Selection([
        ('1', u'Normal'),
        ('2', u'Contingência')],
        required=True,
        string=u'Forma de emissão do MDF-e',
        default='1'
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
    ind_carrega_posterior = fields.Boolean(
        required=False,
        string='Indicador de Carga posterior',
        help=u'Indicador de MDF-e com inclusão da Carga posterior a emissão '
             u'por evento de inclusão de DF-e'
    )
    serie = fields.Many2one(
        string=u'Série',
        comodel_name='br_account.document.serie',
        required=True
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
            # Verificando se só existe uma serie ou mais de uma
            ids_series = self.env.ref('br_mdfe_base.fiscal_document_58').ids
            search_serie = [
                ('fiscal_document_id', 'in', ids_series),
                ('active', '=', True),
                ('company_id', '=', self.emitente.id)
            ]
            serie = self.env['br_account.document.serie'].search(search_serie)
            # Caso exista mais de uma, retorne lista caso contrario escolha ela
            if len(serie) == 1:
                self.serie = serie.id
            return {'domain': {'serie': search_serie}}

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
            mun = self.env['res.state.city']. \
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
            mun = self.env['res.state.city']. \
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

        if 'serie' not in vals:
            raise UserError(u'Serie é obrigatorio')
        serie = self.env['br_account.document.serie'].search(
            [('id', '=', vals['serie'])]
        )
        vals['numero_mdfe'] = serie.internal_sequence_id.next_by_id()
        vals['name'] = 'MDF-e {}'.format(vals['numero_mdfe'])
        vals['codigo_mdfe'] = random.randrange(0, 99999999, 8)
        return super(MdfeEletronic, self).create(vals)

    @api.multi
    def validar_mdfe(self):
        ender_emit = TEndeEmi(
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
        emit = emitType(
            CNPJ=self.emit_cnpj_cpf,
            IE=self.emit_inscr_est,
            xNome=self.emit_nome,
            xFant=self.emit_fantasia,
            enderEmit=ender_emit
        )

        carregamentos = []
        for carregamento in self.inf_mun_carrega:
            carregamento_append = infMunCarregaType(
                cMunCarrega='%s%s' % (
                    carregamento.mun.state_id.ibge_code,
                    carregamento.mun.ibge_code
                ),
                xMunCarrega=carregamento.mun.name
            )
            carregamentos.append(carregamento_append)

        percursos = []
        for percurso in self.inf_percurso:
            if self.inf_mun_carrega[0].code != percurso.code != \
                    self.inf_mun_descarga[0].code:
                percursos.append(infPercursoType(percurso.code))

        chave = self.chave if self.chave is not False else self.monta_chave()
        if self.cdv is not False:
            cdv = str(self.cdv)
        else:
            cdv = str(chave[:len(chave) - 1])

        ide = {
            'cUF': self.emit_uf.ibge_code,
            'tpAmb': self.amb,
            'tpEmit': self.tipo_emitente_mdfe,
            'tpTransp': None if self.tipo_tranpor is False else '1',
            'mod': 58,
            'serie': int(self.serie.code),
            'nMDF': int(self.numero_mdfe),
            'cMDF': self.codigo_mdfe,
            'cDV': cdv,
            'modal': self.modal,
            'tpEmis': self.tipo_emissao,
            'procEmi': '0',
            'verProc': 'Odoo',
            'UFIni': self.inf_mun_carrega[0].mun.state_id.code,
            'UFFim': self.inf_mun_descarga[0].mun.state_id.code,
            'infMunCarrega': carregamentos,
            'infPercurso': percursos,
        }
        tz = timezone(self.env.user.tz)
        if self.data_emissao is False:
            ide['dhEmi'] = \
                datetime.now(tz).replace(microsecond=0).isoformat()
        else:
            dt_emissao = fields.Datetime.from_string(self.data_emissao)
            dt_emissao = tz.localize(dt_emissao).replace(microsecond=0)
            ide['dhEmi'] = dt_emissao.isoformat()

        if self.dh_ini_viagem is not False:
            dh_ini_viagem = fields.Datetime.from_string(self.dh_ini_viagem)
            dh_ini_viagem = tz.localize(dh_ini_viagem).replace(microsecond=0)
            ide['dhIniViagem'] = dh_ini_viagem.isoformat()
        else:
            ide['dhIniViagem'] = ide['dhEmi']

        if self.ind_canal_verde is not False:
            ide['indCanalVerde'] = self.ind_canal_verde

        if self.ind_carrega_posterior is not False:
            ide['indCarregaPosterior'] = self.ind_carrega_posterior
        ide = ideType(**ide)

        # Vamos começar a gerar as infomações de descarga
        descargas = []
        for descarga in self.inf_mun_descarga:
            inf_ctes = []
            inf_nfes = []
            mdfe_transps = []

            for doc in descarga.inf_documents:
                # Tratando unidade de transporte
                inf_unid_transp = []
                for unid in doc.inf_unid_transp:
                    lac_unid_transp = []
                    for lac_unid in unid.lac_unid_transp:
                        x = lacUnidTranspType(
                            nLacre=lac_unid.numero_lacre
                        )
                        lac_unid_transp.append(x)

                    # Tratando unidades de Carga
                    inf_unid_carga = []
                    for unid_carga in unid.inf_unid_carga:
                        lac_unid_carga = []
                        for lac_carga in unid_carga.lac_unid_carga:
                            x = lacUnidCargaType(
                                nLacre=lac_carga.numero_lacre
                            )
                            lac_unid_carga.append(x)

                        x = TUnidCarga(
                            tpUnidCarga=unid_carga.tp_unid_carga,
                            idUnidCarga=unid_carga.id_unid_carga
                            if unid_carga.id_unid_carga is False else None,
                            lacUnidCarga=lac_unid_carga if lac_unid_carga else
                            None,
                            qtdRat=unid_carga.qtd_rat
                            if unid_carga.qtd_rat is False else None
                        )
                        inf_unid_carga.append(x)

                    x = TUnidadeTransp(
                        tpUnidTransp=unid.tp_unid_transp,
                        idUnidTransp=unid.id_unid_transp
                        if unid.qtd_rat is False else None,
                        lacUnidTransp=lac_unid_transp if
                        lac_unid_transp else None,
                        infUnidCarga=inf_unid_carga if inf_unid_carga
                        else None,
                        qtdRat=unid.qtd_rat if unid.qtd_rat is False else None
                    )
                    inf_unid_transp.append(x)

                # Tratando registros de produtos perigosos
                peri_products = []
                for peri in doc.peri:
                    x = periType(
                        nONU=peri.n_onu,
                        xNomeAE=peri.xnome_ae,
                        xClaRisco=peri.xcla_risco,
                        grEmb=peri.gr_emb,
                        qTotProd=peri.q_tot_prod,
                        qVolTipo=peri.q_vol_tipo
                    )
                    peri_products.append(x)

                if doc.tp_document == '1':
                    # Tratando registros de entregas parciais
                    entrega_parcial = []
                    for parcial in doc.inf_entrega_parcial:
                        x = infEntregaParcialType(
                            qtdTotal=parcial.qtd_total,
                            qtdParcial=parcial.qtd_parcial
                        )
                        entrega_parcial.append(x)

                    x = infCTeType(
                        chCTe=doc.chave,
                        SegCodBarra=doc.seg_cod_barra if doc.seg_cod_barra
                        else None,
                        indReentrega=doc.ind_reentrega if doc.ind_reentrega
                        else None,
                        infUnidTransp=inf_unid_transp if inf_unid_transp
                        else None,
                        peri=peri_products if peri_products else None,
                        infEntregaParcial=entrega_parcial if entrega_parcial
                        else None,
                    )
                    inf_ctes.append(x)

                if doc.tp_document == '2':
                    x = infNFeType(
                        chNFe=doc.chave,
                        SegCodBarra=doc.seg_cod_barra if doc.seg_cod_barra
                        else None,
                        indReentrega=doc.ind_reentrega if doc.ind_reentrega
                        else None,
                        infUnidTransp=inf_unid_transp if inf_unid_transp
                        else None,
                        peri=peri_products if peri_products else None,
                    )
                    inf_nfes.append(x)

                if doc.tp_document == '3':
                    x = infMDFeTranspType(
                        chMDFe=doc.chave,
                        indReentrega=doc.ind_reentrega if doc.ind_reentrega
                        else None,
                        infUnidTransp=inf_unid_transp if inf_unid_transp
                        else None,
                        peri=peri_products if peri_products else None,
                    )
                    mdfe_transps.append(x)

            x = infMunDescargaType(
                cMunDescarga='%s%s' % (
                    descarga.mun.state_id.ibge_code,
                    descarga.mun.ibge_code
                ),
                xMunCarrega=descarga.mun.name,
                infCTe=inf_ctes if inf_ctes else None,
                infNFe=inf_nfes if inf_nfes else None,
                infMDFeTransp=mdfe_transps if mdfe_transps else None
            )
            descargas.append(x)
        inf_doc = infDocType(descargas)
        inf_mdfe = infMDFeType(
            versao=3.0,
            Id="MDFe{}".format(chave),
            ide=ide,
            emit=emit,
            infModal=None,
            infDoc=inf_doc,
            seg=None,
            tot=None,
            lacres=None,
            autXML=None,
            infAdic=None,
            infRespTec=None
        )
        mdfe = TMDFe(
            infMDFe=inf_mdfe,
            infMDFeSupl=None,
            Signature=None,
        )
        mdfe.export(sys.stdout, 0)

    def monta_chave(self):
        if self.data_emissao is False:
            tz = timezone(self.env.user.tz)
            dt_emissao = datetime.now(tz).replace(microsecond=0).isoformat()
        else:
            dt_emissao = self.data_emissao.replace(microsecond=0).isoformat()
        chave_parcial = "%s%s%s%s%s%s%d%s" % (
            self.emit_uf.ibge_code, dt_emissao, self.emit_cnpj_cpf, '58',
            self.serie.code.zfill(3), str(self.numero_mdfe).zfill(9),
            int(self.tipo_emissao), self.codigo_mdfe)
        chave_parcial = re.sub('[^0-9]', '', chave_parcial)
        soma = 0
        contador = 2
        for c in reversed(chave_parcial):
            soma += int(c) * contador
            contador += 1
            if contador == 10:
                contador = 2
        dv = (11 - soma % 11) if (soma % 11 != 0 and soma % 11 != 1) else 0
        self.write({
            'chave': chave_parcial + str(dv),
            'cdv': str(dv)
        })
        return chave_parcial + str(dv)
