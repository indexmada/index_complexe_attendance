# -*- coding: utf-8 -*-

import io
from ast import literal_eval

import xlsxwriter as xlsxwriter

from odoo import models, fields, api
from datetime import datetime,date,timedelta

import base64

MONTHS_LIST = ['', 'Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août','Septembre', 'Octobre', 'Novembre', 'Décembre']
DAY_WEEKS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']

class HrAttendance(models.Model):
    _inherit="hr.attendance"

    custom_attendance_image = fields.Binary("Photo")

    def get_interval_date(self):
        d_beg = date.today() 
        day_of_week = d_beg.weekday() #Lundi: 0; Mardi: 1 ....
        while day_of_week != 0:
            d_beg = d_beg-timedelta(days=1)
            day_of_week = d_beg.weekday()

        d_end = date.today()
        day_of_week = d_end.weekday()
        while day_of_week != 6:
            d_end = d_end+timedelta(days=1)
            day_of_week = d_end.weekday()

        return (d_beg, d_end)

    def send_mail_attendance(self):
        print('*'*100)
        x_attendance_user = self.env.company.x_attendance_user
        email_template = self.env.ref("index_complexe_attendance.mail_template_attendance")
        date_today = date.today()

        interval_date = self.get_interval_date()

        if self.env.company.all_the == 'jour':
            date_str = date.today()
        else:
            date_str = str(interval_date[0])+ ' au '+str(interval_date[1])

        # Generate xlsx file
        filename = "Présence_"+str(date_today)+".xlsx"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        self.generate_xlsx_attendace(workbook)  
        workbook.close()
        output.seek(0)

        datas = base64.encodestring(output.read())

        attachment_data = {
            'name':filename,
            'datas':datas,
            'res_model':"hr.attendance",
        }
        generated_file = self.env['ir.attachment'].create(attachment_data)
        # End Generate xlsx file

        email_from = self.env.company.email

        for user in x_attendance_user:
            template_values = {
                'email_from': email_from,
                'email_to': user.email,
                'email_cc': False,
                'auto_delete': True,
                'partner_to': user.partner_id.id,
                'scheduled_date': False,
            }
            email_template.attachment_ids = [(6,0,[generated_file.id])]
            email_template.write(template_values)
            if self.env.company.all_the == 'jour':
                day_week = "ce jour"
            else:
                day_week = "cette semaine"
            context = {
                'lang': self.env.user.lang,
                'date_str': date_str,
                'user_name': user.name,
                'day_week': day_week
            }
            with self.env.cr.savepoint():
                email_template.with_context(context).send_mail(user.id, force_send=True, raise_exception=True)
                values = email_template.generate_email(user.id)

        return True

    def generate_xlsx_attendace(self, workbook):
        interval_date = self.get_interval_date()
        bold_center_13 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": 13,
            'bold': True,
        })
        cell_center_11 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 11,
            "bold": False,
        })
        cell_left_11 = workbook.add_format({
            'align': 'left',
            'valign': 'vleft',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 11,
            "bold": False,
        })

        cell_center_bol_red_11 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 11,
            "bold": True,
            "color": "red",
        })
        cell_center_bol_green_11 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 11,
            "bold": True,
            "color": "green",
        })

        cell_bold_center_11 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 11,
            "bold": True,
        })
        date_begin = interval_date[0]
        if self.env.company.all_the == 'jour':
            range_tab = [date.today().weekday()]
            current_date = date.today()
        else:
            range_tab = range(0,6)
            current_date = date_begin
        for i in range_tab:
            employee_ids = self.env['hr.employee'].sudo()

            worksheet_ost = workbook.add_worksheet(DAY_WEEKS[i])
            self.style(worksheet_ost)
            d1 = current_date
            str_date_beg = str(d1.day)+' '+MONTHS_LIST[d1.month]+' '+str(d1.year)
            # Sheet header:
            worksheet_ost.merge_range('A1:E1', 'Présences: '+str_date_beg, bold_center_13)
            worksheet_ost.write('A3','Date',cell_bold_center_11)
            worksheet_ost.write('B3','Nom',cell_bold_center_11)
            worksheet_ost.write('C3','Heure Entrée',cell_bold_center_11)
            worksheet_ost.write('D3','Heure Sortie',cell_bold_center_11)
            worksheet_ost.write('E3','Heure Total',cell_bold_center_11)      

            hr_leave_ids = self.env['hr.leave'].sudo().search([('date_from', '<=', current_date), ('date_to', '>=', current_date), ('state', '=', 'validate')])

            attendance_ids = self.search([]).filtered(lambda att: att.check_in.date() == current_date)
            row = 4
            for attendance in attendance_ids:

                employee_ids |= attendance.employee_id

                check_in = attendance.check_in
                check_out = attendance.check_out
                if check_out:
                    total = check_out - check_in
                    total_formated = self.format_total_time(total)
                    check_out = check_out.strftime("%H:%M:%S")
                else:
                    check_out = 'Non pointé'
                    total_formated = '0'

                date_att = str(check_in.day) +' '+MONTHS_LIST[check_in.month]+' '+str(check_in.year)

                cell = 'A'+str(row)
                worksheet_ost.write(cell, date_att, cell_center_11)
                cell = 'B'+str(row)
                worksheet_ost.write(cell, attendance.employee_id.name, cell_left_11)
                cell = 'C'+str(row)
                # check-in +3
                check_in = check_in.strftime("%H:%M:%S")
                in_splited = str(check_in).split(':')
                check_in_inc = str(int(in_splited[0])+3)+':'+in_splited[1]+':'+in_splited[2]
                worksheet_ost.write(cell,check_in_inc, cell_center_11)

                cell = 'D'+str(row)
                # check-out +3
                if check_out != 'Non pointé':
                    out_splited = str(check_out).split(':')
                    check_out_inc = str(int(out_splited[0])+3)+':'+out_splited[1]+':'+out_splited[2]
                else:
                    check_out_inc = 'Non pointé'
                worksheet_ost.write(cell, check_out_inc,cell_center_11)
                cell = 'E'+str(row)
                worksheet_ost.write(cell,total_formated, cell_center_11)
                row += 1

            if len(employee_ids) > 0:
                absent_employee_ids = self.env['hr.employee'].sudo().search([('id','not in', employee_ids.ids)])
                for employee in absent_employee_ids:
                    cell = 'A'+str(row)
                    worksheet_ost.write(cell, date_att, cell_center_11)
                    cell = 'B'+str(row)
                    worksheet_ost.write(cell, employee.name, cell_left_11)
                    cell = 'C'+str(row)
                    worksheet_ost.write(cell,'', cell_center_11)
                    cell = 'D'+str(row)
                    worksheet_ost.write(cell, '',cell_center_11)
                    cell = 'E'+str(row)
                    if employee in hr_leave_ids.mapped('employee_id'):
                        worksheet_ost.write(cell,'CONGÉ', cell_center_bol_green_11)
                    else:
                        worksheet_ost.write(cell,'ABSENT', cell_center_bol_red_11)
                    row += 1

            current_date = current_date + timedelta(days=1)

    def style(self, worksheet):
        worksheet.set_column('A:T', 14)

    def format_total_time(self, timedelta):
        result = ''
        if timedelta.days:
            jr = timedelta.days
            result += str(jr)+'j '
        if timedelta.seconds:
            sec = timedelta.seconds
            mn = int(sec / 60)
            reste_sec = sec%60

            hr = int(mn/60)
            reste_mn = mn%60

            if hr:
                result += str(hr)+'h'
            if reste_mn:
                result += ' '+str(reste_mn)+'mn'
            if reste_sec:
                result += ' '+str(reste_sec)+'s'

        return result


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

    def check_webcam_enabled(self):
        return self.env.company.enable_webcam