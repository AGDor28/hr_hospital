from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class DiseaseReportWizard(models.TransientModel):
    """A transient wizard to generate analytical reports filtered by diseases and doctors.

    Provides parameters to define a time window, specific medical staff, and precise
    illnesses. It dynamic builds standard filters to display aggregate statistics in
    pivot, list, or form representations.
    """
    _name = 'hr.hospital.disease.report.wizard'
    _description = 'Disease Report Wizard'

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: date.today().replace(day=1)
    )

    date_to = fields.Date(
        string='Date To',
        required=True,
        default=lambda self: date.today() + relativedelta(day=31)
    )

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors',
    )
    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diseases',
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-populates configuration parameters using active user context records.

        If launching directly from a specific doctor's profile or form action view,
        this method intercepts the active background IDs to pre-select that doctor
        within the wizard fields.

        Args:
            fields_list (list[str]): Names of the fields configured on the model
                requesting baseline initialization.

        Returns:
            dict: Standard initialization mappings, potentially including selected
                doctor reference command tuples.
        """
        res = super().default_get(fields_list)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')

        if active_model == 'hr.hospital.doctor' and active_ids:
            res['doctor_ids'] = [(6, 0, active_ids)]

        return res

    def action_generate_report(self):
        """Compiles search filters and redirects to a grouped dashboard of matching visits.

        Evaluates chronological constraints along with selected relational fields
        to launch a custom filtered Action window.

        Returns:
            dict: An ir.actions.act_window configuration structure pointing to
                the visits ledger, set to automatically group rows by disease category.
        """
        self.ensure_one()

        domain = [
            ('planned_date', '>=', self.date_from),
            ('planned_date', '<=', self.date_to)
        ]

        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))

        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))

        return {
            'name': 'Disease Report',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,pivot,form',
            'domain': domain,
            'context': {'group_by': 'disease_id'},
            'target': 'current',
        }
