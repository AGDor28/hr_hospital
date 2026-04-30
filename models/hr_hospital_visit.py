import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HospitalVisit(models.Model):
    _name = "hr.hospital.visit"
    _description = "Patient Visit"

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

    status = fields.Selection([
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ],
        string='Status',
        default='planned',
        required=True
    )

    planned_date = fields.Datetime(
        string='Planned Date',
        required=True,
        help="Scheduled time for the visit"
    )

    visit_date = fields.Datetime(
        string='Actual Visit Date',
    )

    summary = fields.Html(string='Summary / Epicrisis')

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Diagnosis / Disease'
    )

    active = fields.Boolean(default=True)

    def unlink(self):
        for obj in self:
            if obj.status == 'completed':
                raise UserError("You cannot delete a visit that has already taken place.")
        return super(HospitalVisit, self).unlink()

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            for obj in self:
                if obj.status == 'completed':
                    raise UserError("You cannot archive a visit that has already taken place.")
        return super(HospitalVisit, self).write(vals)