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
    _inherit = 'mdfe.eletronic'

    modal_rodoviario = fields.One2many(
        comodel_name='modal.rodoviario',
        inverse_name='mdfe',
        string="Informações do Modal Rodoviario",
    )
