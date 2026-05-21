import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

class HospitalMassReassignDoctor(models.TransientModel):
    """An administrative utility wizard to execute bulk transfers of patient rosters.

    Designed to handle personnel reshuffling or shift handovers by processing
    a collection of selected patients, closing out their current active primary
    physician history timelines, assigning a new physician, and recording audit
    logs in a single operation.
    """
    _name = 'hr.hospital.mass.reassign.doctor.wizard'
    _description = 'Mass Reassign Doctor'

    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='New Doctor',
        required=True
    )

    reassignment_date = fields.Date(
        string='Updated At',
        default=fields.Date.today,
    )

    def reassign_doctor(self):
        """Processes and alters historical assignments for a collection of selected patients.

        Extracts patient indices from execution context arrays, sets termination
        dates on lingering open historical records, remaps the patient master profiles,
        and initializes new active doctor history rows. Skips execution if the target
        doctor is already assigned as the primary provider.

        Returns:
            None: Concludes routine execution silently after processing batch data updates.
        """
        active_patient_ids = self.env.context.get('active_ids')
        if not active_patient_ids or not self.new_doctor_id:
            return

        patients = self.env['hr.hospital.patient'].browse(active_patient_ids)

        old_histories = self.env['hr.hospital.doctor.history'].search([
            ('patient_id', 'in', patients.ids),
            ('active', '=', True),
            ('reassignment_date', '=', False)
        ])

        if old_histories:
            old_histories.write({
                'reassignment_date': self.reassignment_date,
            })

        for patient in patients:
            if patient.personal_doctor_id == self.new_doctor_id:
                continue

            patient.personal_doctor_id = self.new_doctor_id

            self.env['hr.hospital.doctor.history'].create([{
                'patient_id': patient.id,
                'doctor_id': self.new_doctor_id.id,
                'assignment_date': self.reassignment_date,
                'active': True
            }])

        return
