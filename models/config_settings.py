# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_webcam = fields.Boolean(string="Activer Webcam", related="company_id.enable_webcam",readonly=False, config_parameter="att.enable_webcam")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('att.enable_webcam', self.env.company.enable_webcam)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['enable_webcam'] = self.env.company.enable_webcam
        return res