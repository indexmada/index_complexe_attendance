odoo.define('web_widget_image_webcam.kiosk_confirm', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var field_utils = require('web.field_utils');
var QWeb = core.qweb;
var Dialog = require('web.Dialog');
var _t = core._t;
var rpc = require('web.rpc');
var time = require('web.time');


var KioskConfirm = AbstractAction.extend({
    events: {
        "click .o_hr_attendance_back_button": function () { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
        "click .o_form_binary_file_web_cam_complexe":  _.debounce(function() {
            var self = this
            this._rpc({
                    model: 'hr.employee',
                    method: 'check_webcam_enabled',
                    args: [[this.employee_id]],
                })
                .then(function(result) {
                    if (result) {
                        self.webcam_attendance();
                    }
                    else {
                        var def = self._rpc({
                                model: 'hr.employee',
                                method: 'create_time_checkin_checkout_new',
                                args: [[self.employee_id], self.next_action],
                                kwargs: {
                                    'image_attendance': '',
                                },
                            }).then(function(result) {
                                if (result.action) {
                                    self.do_action(result.action);
                                } else if (result.warning) {
                                    self.do_warn(result.warning);
                                }
                            });
                    }
                });
        },
         200, true),
        "click .o_hr_attendance_sign_in_out_icon": _.debounce(function () {
            var self = this;
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[this.employee_id], this.next_action],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        }, 200, true),
        'click .o_hr_attendance_pin_pad_button_0': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 0); },
        'click .o_hr_attendance_pin_pad_button_1': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 1); },
        'click .o_hr_attendance_pin_pad_button_2': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 2); },
        'click .o_hr_attendance_pin_pad_button_3': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 3); },
        'click .o_hr_attendance_pin_pad_button_4': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 4); },
        'click .o_hr_attendance_pin_pad_button_5': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 5); },
        'click .o_hr_attendance_pin_pad_button_6': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 6); },
        'click .o_hr_attendance_pin_pad_button_7': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 7); },
        'click .o_hr_attendance_pin_pad_button_8': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 8); },
        'click .o_hr_attendance_pin_pad_button_9': function() { this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 9); },
        'click .o_hr_attendance_pin_pad_button_C': function() { this.$('.o_hr_attendance_PINbox').val(''); },
        'click .o_hr_attendance_pin_pad_button_ok': _.debounce(function() {
            var self = this;
            this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[this.employee_id], this.next_action, this.$('.o_hr_attendance_PINbox').val()],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                        self.$('.o_hr_attendance_PINbox').val('');
                        setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                    }
                });
        }, 200, true),
    },

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        this.employee_id = action.employee_id;
        this.employee_name = action.employee_name;
        this.employee_state = action.employee_state;
        this.employee_hours_today = field_utils.format.float_time(action.employee_hours_today);
    },

    start: function () {
        var self = this;
        this.getSession().user_has_group('hr_attendance.group_hr_attendance_use_pin').then(function(has_group){
            self.use_pin = has_group;
            self.$el.html(QWeb.render("HrAttendanceKioskConfirm", {widget: self}));
            self.start_clock();
        });
        return self._super.apply(this, arguments);
    },

    start_clock: function () {
        this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));}, 500);
        // First clock refresh before interval to avoid delay
        this.$(".o_hr_attendance_clock").show().text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
    },

    destroy: function () {
        clearInterval(this.clock_start);
        this._super.apply(this, arguments);
    },

    webcam_attendance: function () {
           var self = this,
           WebCamDialog = $(QWeb.render("WebCamDialog")),
           img_data;

           Webcam.set({
                width: 320,
                height: 240,
                dest_width: 320,
                dest_height: 240,
                image_format: 'jpeg',
                jpeg_quality: 90,
                force_flash: false,
                fps: 45,
                swfURL: '/web_widget_image_webcam/static/src/js/webcam.swf',
            });

           var dialog = new Dialog(self, {
                size: 'large',
                dialogClass: 'o_act_window',
                title: _t("WebCam Booth"),
                $content: WebCamDialog,
                buttons: [
                    {
                        text: _t("Prendre une photo"), classes: 'btn-primary take_snap_btn fa fa-camera',
                        click: function () {
                            Webcam.snap( function(data) {
                                img_data = data;
                                // Display Snap besides Live WebCam Preview
                                WebCamDialog.find("#webcam_result").html('<img src="'+img_data+'"/>');
                            });
                            var img_data_base64 = img_data.split(',')[1];
                            // if (self.employee_state == 'checked_out'){
                            var identifier = Math.random().toString(36).substr(2, 5);
                            var def = this._rpc({
                                model: 'hr.employee',
                                method: 'create_time_checkin_checkout_new',
                                args: [[self.employee_id], self.next_action],
                                kwargs: {
                                    'image_attendance': img_data_base64,
                                    'identifier': identifier
                                },
                            }).then(function(result) {
                                if (result.action) {
                                    self.do_action(result.action);
                                } else if (result.warning) {
                                    self.do_warn(result.warning);
                                }
                            });
                        }
                    },
                    {
                        text: _t("Close"), close: true
                    }
                ]
            }).open();

            dialog.opened().then(function() {
                    Webcam.attach('#live_webcam');

                    // Placeholder Image in the div "webcam_result"
                    WebCamDialog.find("#webcam_result").html('<img src="/index_attendance_face_recognition/static/src/img/webcam_placeholder.png"/>');
                });
        }
});

core.action_registry.add('hr_attendance_kiosk_confirm', KioskConfirm);

return KioskConfirm;

});
