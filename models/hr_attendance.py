# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class HrAttendance(models.Model):
    _inherit="hr.attendance"

    custom_attendance_image = fields.Binary("Photo")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def create_time_checkin_checkout_new(self, next_action, *args, **kwargs):
        # Function called by dialog
        param = kwargs
        employee_id = self
        if employee_id:
            # attendance = employee_id._attendance_action_change()
            res = employee_id.attendance_manual(next_action)
            print('*'*100)
            try:
                attendance_id = int(res['action']['attendance']['id'])
                attendance = self.env['hr.attendance'].sudo().browse(attendance_id)
                attendance.sudo().write({"custom_attendance_image": param.get('image_attendance')})
                print(attendance)
            except:
                {'warning': 'Ooops! Désolé, nous avons rencontré un problème!'}

            return res
        else:
            return {'warning': 'Ooops! Désolé, nous avons rencontré un problème!'}