# Copyright 2016 Siddharth Bhalgami <siddharth.bhalgami@gmail.com>
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Complexe Attendance",
    "summary": "Allows to take image with WebCam",
    "version": "12.0.1.0.0",
    "category": "web",
    "website": "https://github.com/OCA/web",
    "author": "Nampoina Ramarijaona, "
              "Index Consulting, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "data": [
        "views/assets.xml",
        "views/hrAttendance.xml",
        "views/res_company.xml",
        "views/cron.xml",
        "views/email_template.xml",
        "views/config_settings_view.xml",
        'views/work_entry_type.xml',
        'views/resource_calendar.xml',
    ],
    "depends": [
        "base",
        "web",
        "hr_attendance",
        "hr_contract", 
        "hr_work_entry",
        "resource"
    ],
    "qweb": [
        "static/src/xml/web_widget_image_webcam.xml",
    ],
    "installable": True,
}
