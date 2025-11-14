# -*- coding: utf-8 -*-
from odoo import models, fields

class OdooOpenAIProcessed(models.Model):
    _name = 'odoo.openai.processed'
    _description = 'Registra mensajes procesados por Odoo OpenAI Bot'

    message_id = fields.Integer(string='Mail Message ID', required=True, index=True)
