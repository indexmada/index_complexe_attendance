# -*- coding: utf-8 -*-

from odoo import models, fields, api


class resourceCalendar(models.Model):
	_inherit="resource.calendar"

	night_from = fields.Float("Night From")
	night_to = fields.Float("Night To")

class resourceCalendarAttendance(models.Model):
	_inherit = 'resource.calendar.attendance'

	work_entry_type_id = fields.Many2one(comodel_name="hr.work.entry.type", string="Majoration",domain="[('sunday_maj', '=', True)]")