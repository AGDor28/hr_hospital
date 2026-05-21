import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

class HospitalPatient(models.Model):
    """Represents a patient under medical care within the hospital ecosystem.

    This model stores comprehensive patient tracking records, clinical histories,
    associated historical or primary doctors, active medical conditions, and
    provides metrics on scheduled appointments.
    """
    _name = 'hr.hospital.patient'
    _description = 'Patient'

    _inherit = ['hr.hospital.medic.info']

    _inherits = {'res.users': 'user_id'}

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Patient User',
        required=True,
        ondelete='cascade'
    )

    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diseases'
    )

    visit_ids = fields.One2many(
        comodel_name='hr.hospital.visit',
        inverse_name='patient_id',
        string='Visits'
    )

    doctor_history_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.history',
        inverse_name='patient_id',
        string='Doctor history'
    )

    personal_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Personal Doctor',
    )

    insurance_number = fields.Char(
        string='Insurance number',
        size=20
    )

    visit_count = fields.Integer(
        string='Visit Count',
        compute='_compute_visit_count'
    )

    def action_view_patient_visits(self):
        """Navigates to a full, filtered list view of all visits linked to this patient.

        Returns:
        dict: An ir.actions.act_window action targeting the list, form,
        and calendar layouts filtered entirely to the patient's record id.
        """
        self.ensure_one()
        return {
            'name': 'Patient Visits',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form,calendar',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'target': 'current',
        }

    def _compute_visit_count(self):
        """Calculates the total aggregate count of all medical appointments for the patient.

        Used primarily for smart-buttons inside the patient form UI.
        """
        for record in self:
            record.visit_count = len(record.visit_ids)

    def action_create_new_visit(self):
        """Launches a quick creation wizard for scheduling an upcoming appointment.

        Automatically defaults the primary personal doctor (if assigned) and
        sets the baseline state to 'planned'.

        Returns:
        dict: Window action configuration dictionary targeting a clean form popup.
        """
        self.ensure_one()
        return {
            'name': 'Create Visit',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.id,
                'default_doctor_id': self.personal_doctor_id.id if self.personal_doctor_id else False,
                'default_status': 'planned',
            }
        }
