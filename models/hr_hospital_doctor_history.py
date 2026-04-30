import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

CONST_EXP = "Hospital constant example"

class HospitalDoctorHistory(models.Model):
    _name = "hr.hospital.doctor.history"
    _description = "History"

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True,
    )

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
    )

    assignment_date = fields.Date(
        string='Assignment Date',
        required=True,
        default=fields.Date.today()
    )

    reassignment_date = fields.Date(
        string='Reassignment Date',
    )

    active = fields.Boolean(
        default=True,
    )

    @api.onchange('assignment_date', 'reassignment_date')
    def _onchange_dates_check(self):
        if self.assignment_date and self.reassignment_date:
            if self.reassignment_date < self.assignment_date:
                self.reassignment_date = False
                return {
                    'warning': {
                        'title': "Warning",
                        'message': "Reassignment date cannot be earlier than the assignment date"
                    }
                }
        return None

    @api.depends('patient_id.name', 'doctor_id.name', 'doctor_id.category_id.name', 'assignment_date')
    def _compute_display_name(self):
        for obj in self:
            patient_name = obj.patient_id.name
            doctor_name = obj.doctor_id.name
            doctor_category = f"({obj.doctor_id.category_id.name})" if obj.doctor_id.category_id else ""
            a_date = obj.assignment_date or ""
            obj.display_name = f"{patient_name} - {doctor_name} {doctor_category} {a_date}".strip()

    @api.model_create_multi
    def create(self, vals_list):
        records = super(HospitalDoctorHistory, self).create(vals_list)

        for rec in records:
            if rec.active and rec.patient_id and rec.doctor_id:
                rec.patient_id.write({
                    'personal_doctor': rec.doctor_id.id
                })

        return records