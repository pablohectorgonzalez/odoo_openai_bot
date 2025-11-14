# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openai_api_key = fields.Char(string='OpenAI API Key')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env['ir.config_parameter'].sudo()
        res['openai_api_key'] = icp.get_param('odoo_openai_bot.api_key', default='')
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param('odoo_openai_bot.api_key', self.openai_api_key or '')
