import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HospitalVisit(models.Model):
    _name = "hr.hospital.visit"
    _description = "Patient Visit"

    visit_date = fields.Datetime(string='Visit Date', default=fields.Datetime.now)

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True
    )

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True
    )