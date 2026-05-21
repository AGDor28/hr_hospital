import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class HospitalVisitReport(models.TransientModel):
    """A detailed multi-criteria search wizard to extract clinical transaction records.

    Allows back-office operators or administrative chiefs to build custom cross-sections
    of data by intersecting arbitrary arrays of doctors, patients, dates, completed
    statuses, and exact medical diagnoses.
    """
    _name = 'hr.hospital.visit.report.wizard'
    _description = 'Visit Report'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
    )

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Patient',
    )

    date_from = fields.Date(
        string='Start Period',
    )

    date_to = fields.Date(
        string='End Period',
    )

    only_completed = fields.Boolean(
        string='Only Completed Visits'
    )

    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diseases'
    )

    @api.model
    def default_get(self, fields_list):
        """Interceptors operational context parameters to dynamically seed filters on startup.

        Detects whether this reporting popup was triggered from a patient dashboard
        or a medical practitioner ledger, automatically populating the corresponding
        filter parameter to streamline user interaction.

        Args:
            fields_list (list[str]): Names of the fields configured on the model
                requesting baseline initialization.

        Returns:
            dict: Initial values dictionary containing contextual structural mappings.
        """
        res = super().default_get(fields_list)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')

        if active_model == 'hr.hospital.patient' and active_ids:
            res['patient_ids'] = [(6, 0, active_ids)]
        elif active_model == 'hr.hospital.doctor' and active_ids:
            res['doctor_ids'] = [(6, 0, active_ids)]

        return res

    def action_generate_report(self):
        """Assembles user constraints into a search domain and opens the resulting visit logs.

        Dynamically checks every criteria field to formulate precise database lookup clauses,
        evaluating conditions based on actual clinical observation execution dates.

        Returns:
            dict: Window action configuration dictionary mapping to the matching
                    hr.hospital.visit` views.
        """
        self.ensure_one()

        domain = []

        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))

        if self.patient_ids:
            domain.append(('patient_id', 'in', self.patient_ids.ids))

        if self.date_from:
            domain.append(('visit_date', '>=', self.date_from))

        if self.date_to:
            domain.append(('visit_date', '<=', self.date_to))

        if self.only_completed:
            domain.append(('status', '=', 'completed'))

        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))

        return {
            'name': 'Filtered Visits',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }
