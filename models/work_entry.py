# -*- coding: utf-8 -*-

from odoo import models, fields, api


class workEntryType(models.Model):
	_inherit = 'hr.work.entry.type'

	sunday_maj = fields.Boolean("Dimanche")
	holiday_maj = fields.Boolean("Jours Fériés")