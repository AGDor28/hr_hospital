import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class HospitalVisitReport(models.TransientModel):
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

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Disease'
    )

    @api.model
    def default_get(self, fields_list):
        res = super(HospitalVisitReport, self).default_get(fields_list)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')

        if active_model == 'hr.hospital.patient' and active_ids:
            res['patient_ids'] = [(6, 0, active_ids)]
        elif active_model == 'hr.hospital.doctor' and active_ids:
            res['doctor_ids'] = [(6, 0, active_ids)]

        return res

    def action_generate_report(self):
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

        if self.disease_id:
            domain.append(('disease_id', 'in', self.disease_id.id))

        return {
            'name': 'Filtered Visits',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }
