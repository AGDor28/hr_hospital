import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

CONST_EXP = "Hospital constant example"

class HospitalDoctorHistory(models.Model):
    """Tracks historical reassignments and timelines of personal doctors for patients.

    Maintains a continuous record of when a physician was assigned to a patient
    and when they were replaced, while automatically synchronization changes back
    to the active patient profile.
    """
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
        default=fields.Date.today
    )

    reassignment_date = fields.Date(
        string='Reassignment Date',
    )

    active = fields.Boolean(
        default=True,
    )

    @api.onchange('assignment_date', 'reassignment_date')
    def _onchange_dates_check(self):
        """Performs a real-time logical chronological validation on historical dates.

        Prevents users from setting an end/reassignment date that occurs prior to
        the initial assignment date.

        Returns:
        dict or None: A warning structure that resets the invalid reassignment date
        field back to False if a chronological error is caught, otherwise None.
        """
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
        """Constructs an analytical tracking name for history entries.

        Synthesizes patient context, physician profile details, rank categories, and
        the effective relationship starting date.
        Example output: "John Doe - Dr. Smith (Senior Consultant) 2026-05-20"
        """
        for obj in self:
            patient_name = obj.patient_id.name
            doctor_name = obj.doctor_id.name
            doctor_category = f"({obj.doctor_id.category_id.name})" if obj.doctor_id.category_id else ""
            a_date = obj.assignment_date or ""
            obj.display_name = f"{patient_name} - {doctor_name} {doctor_category} {a_date}".strip()

    @api.model_create_multi
    def create(self, vals_list):
        """Extends batch record creation to synchronize active personal doctor assignments.

        When a new active history line is created, this method automatically updates
        the `personal_doctor_id` on the corresponding patient's master file to match
        the newly assigned doctor.

        Args:
            vals_list (list[dict]): A list of dictionaries containing field values
                for initializing new history records.

        Returns:
            models.Recordset: The newly generated history records recordset.
        """
        records = super().create(vals_list)

        for rec in records:
            if rec.active and rec.patient_id and rec.doctor_id:
                rec.patient_id.write({
                    'personal_doctor_id': rec.doctor_id.id
                })

        return records
