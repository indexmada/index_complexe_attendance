# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_new_worked_days_lines(self):
        if self.struct_id.use_worked_day_lines:
            # computation of the salary worked days
            worked_days_line_values = self._get_worked_day_lines()

            # Majoration Dimanche
            sunday_increase = self._get_sunday_increase()
            if sunday_increase:
                worked_days_line_values.append(sunday_increase)

            # Majoration Jour Férié
            holiday_maj = self._get_holiday_maj()

            worked_days_lines = self.worked_days_line_ids.browse([])
            for r in worked_days_line_values:
                worked_days_lines |= worked_days_lines.new(r)
            return worked_days_lines
        else:
            return [(5, False, False)]

    def _get_sunday_increase(self):
        # Temps de travail: resource.calendar
        calendar_id = self.employee_id.resource_calendar_id
        is_sunday_increased = calendar_id.attendance_ids.filtered(lambda at: at.work_entry_type_id)
        paid_amount = self._get_contract_wage()

        res = False

        if is_sunday_increased:
            domain = [('employee_id', '=', self.employee_id.id)]
            sunday_attendance_ids = self.env['hr.attendance'].sudo().search(domain).filtered(lambda att: (att.check_in.date() >= self.date_from) and (att.check_in.date() <= self.date_to) and (att.check_in.date().weekday() == 6) )
            if sunday_attendance_ids:
                work_entry_type = is_sunday_increased[0].work_entry_type_id

                # Number of hours
                nb_hours = sum(sund_worked.worked_hours for sund_worked in sunday_attendance_ids )

                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': '',
                    'number_of_hours': nb_hours,
                    'amount': paid_amount *0.4,
                }
                res = attendance_line

        return res


