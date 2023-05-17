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
        "views/email_template.xml"
    ],
    "depends": [
        "base",
        "web",
        "hr_attendance",
    ],
    "qweb": [
        "static/src/xml/web_widget_image_webcam.xml",
    ],
    "installable": True,
}
