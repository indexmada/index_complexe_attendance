# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


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
                attendance = res['action']['attendance']
                print(attendance)
            except:
                print('Nooo')

            return res
        else:
            return {'warning': 'Ooops! Désolé, nous avons rencontré un problème!'}