# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime



class Company(models.Model):
    _inherit = 'res.company'

    x_attendance_user = fields.Many2many(string='Déstinataire du corrier(présence)', comodel_name="res.users")
    all_the = fields.Selection(string="Envoyer par",selection=[('jour', 'Jour'), ('semaine', 'Semaine')], default='jour')

    enable_webcam = fields.Boolean(string="Activer Webcam",default=False)

