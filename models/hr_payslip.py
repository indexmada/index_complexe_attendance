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
            if holiday_maj:
                worked_days_line_values.append(holiday_maj)

            # Majoration Nuit
            night_maj = self._get_night_maj()
            if night_maj:
                worked_days_line_values.append(night_maj)

            worked_days_lines = self.worked_days_line_ids.browse([])
            for r in worked_days_line_values:
                worked_days_lines |= worked_days_lines.new(r)
            return worked_days_lines
        else:
            return [(5, False, False)]

    def _get_night_maj(self):
        calendar_id = self.employee_id.resource_calendar_id
        paid_amount = self._get_contract_wage()

        night_we_type_id = self.env['hr.work.entry.type'].sudo().search([('night_maj', '=', True)], limit=1)
        res = False
        if calendar_id.night_from and calendar_id.night_to and night_we_type_id:
            night_from = calendar_id.night_from
            night_to = calendar_id.night_to
            domain = [('employee_id', '=', self.employee_id.id)]
            attendance_ids = self.env['hr.attendance'].sudo().search(domain).filtered(lambda att: 
                (att.check_in and att.check_out) and (
                    ((self._get_float_time(att.check_in.time()) >= night_from) and (self._get_float_time(att.check_in.time()) <= night_to)) or (
                        ((self._get_float_time(att.check_out.time()) >= night_from) and (self._get_float_time(att.check_out.time())) <= night_to)) 
                    )
                )
            nb_hours = 0
            for attendance in attendance_ids:
                check_in = self._get_float_time(attendance.check_in.time())
                check_out = self._get_float_time(attendance.check_out.time())
                nb_hours += min(check_out, night_to) - max(check_in, night_from)

            attendance_line = {
                    'sequence': night_we_type_id.sequence,
                    'work_entry_type_id': night_we_type_id.id,
                    'number_of_days': '',
                    'number_of_hours': nb_hours,
                    'amount': paid_amount *0.1,
            }
            res = attendance_line if nb_hours else False     

        return res

    def _get_float_time(self, time):
        return time.hour + time.minute/60.0

    def _get_holiday_maj(self):
        calendar_id = self.employee_id.resource_calendar_id
        global_leave_ids = calendar_id.global_leave_ids.filtered(lambda leave: leave.date_from.date().month == self.date_from.month)
        maj_leave = self.env['hr.work.entry.type'].sudo().search([('holiday_maj', '=', True)], limit=1)
        res = False
        paid_amount = self._get_contract_wage()
        if global_leave_ids and maj_leave:
            nb_hours = 0
            for gl in global_leave_ids:
                domain = [('employee_id', '=', self.employee_id.id)]
                attendance_ids = self.env['hr.attendance'].sudo().search(domain).filtered(lambda att: (att.check_in and att.check_out)  and (((att.check_in >= gl.date_from) and (att.check_in <= gl.date_to)) or ((att.check_out >= gl.date_from) and (att.check_out <= gl.date_to))))
                for att in attendance_ids:
                    overlap = min(att.check_out, gl.date_to) - max(att.check_in, gl.date_from)
                    nb_hours += overlap.total_seconds()/3600

            attendance_line = {
                    'sequence': maj_leave.sequence,
                    'work_entry_type_id': maj_leave.id,
                    'number_of_days': '',
                    'number_of_hours': nb_hours,
                    'amount': paid_amount *0.1,
            }
            res = attendance_line if nb_hours else False

        return res


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


