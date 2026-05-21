import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class HospitalVisit(models.Model):
    """Manages scheduled appointments, consultations, and outcomes between doctors and patients.

    This model serves as the core ledger of interaction records, holding dates,
    diagnoses (diseases), notes/epicrisis summaries, and workflow progression states
    (planned, completed, cancelled).
    """
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
        string='Disease'
    )

    active = fields.Boolean(default=True)

    @api.constrains('doctor_id', 'planned_date', 'visit_date', 'status')
    def _check_completed_visit_changes(self):
        """Enforces a strict lock state on completed visits.

        Once a consultation transitions to the 'completed' state, critical metadata
        such as assigned specialist, original schedule date, or actual execution date
        cannot be altered to prevent retroactive record falsification.

        Raises:
        ValidationError: If any key field drops alignment with its original
        database state once marked 'completed'.
        """
        for record in self:
            if record._origin.status == 'completed':
                if (record.doctor_id != record._origin.doctor_id or
                        record.planned_date != record._origin.planned_date or
                        record.visit_date != record._origin.visit_date):
                    raise ValidationError(
                        "You cannot modify the Doctor or Dates of a visit that has already been completed."
                    )

    def unlink(self):
        """Overrides standard delete routine to safeguard archived medical items.

        Prevents purging consultations that reached absolute completion status.

        Raises:
        UserError: If any record within the selected deletion batched arrays
        has a status of 'completed'.
        """
        for obj in self:
            if obj.status == 'completed':
                raise UserError("You cannot delete a visit that has already taken place.")
        return super().unlink()

    def write(self, vals):
        """Overrides standard write routine to enforce strict operational data integrity.

        Intercepts data modification streams to safeguard historical clinic interactions.
        If a consultation is already marked as 'completed', this method blocks both
        soft-deletion (archival via the 'active' flag) and retroactive alteration of critical
        metadata—such as the assigned specialist, original schedule date, or actual execution timestamp.

        Raises:
        UserError: If attempting to archive ('active': False) a record that has already taken place.
        ValidationError: If attempting to alter the physician or scheduling fields on a completed visit.
        """
        if 'active' in vals and not vals['active']:
            for obj in self:
                if obj.status == 'completed':
                    raise UserError("You cannot archive a visit that has already taken place.")

        if 'doctor_id' in vals or 'planned_date' in vals or 'visit_date' in vals:
            for obj in self:
                if obj.status == 'completed':
                    raise ValidationError(
                        "You cannot modify the Doctor or Dates of a visit that has already been completed."
                    )
        return super().write(vals)

    @api.depends('doctor_id', 'planned_date', 'patient_id')
    def _compute_display_name(self):
        """Builds a comprehensive name representation string for individual visit records.

        Combines the physician name, associated patient, and formatted calendar date.
        Example output: "Dr. Smith (John Doe) - 2026-05-20 14:00"
        """
        for record in self:
            name = f"{record.doctor_id.name}"
            if record.patient_id:
                name += f" ({record.patient_id.name})"
            if record.planned_date:
                name += f" - {record.planned_date.strftime('%Y-%m-%d %H:%M')}"
            record.display_name = name

    def action_view_similar_disease_visits(self):
        """Opens a dashboard displaying all patients suffering from or assigned the same diagnosis.

        Useful for general analytics or observing epidemic trends of identical diseases
        across multiple historical clinic interactions.

        Returns:
        dict: An ir.actions.act_window action showing visits matching this record's disease.
        """
        self.ensure_one()
        return {
            'name': 'Visits with Same Disease',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': [('disease_id', '=', self.disease_id.id)],
            'context': {'default_disease_id': self.disease_id.id},
            'target': 'current',
        }
