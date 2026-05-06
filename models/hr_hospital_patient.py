import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class HospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'

    _inherit = ['hr.hospital.medic.info']

    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Patient',
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

    personal_doctor = fields.Many2one(
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
        for record in self:
            record.visit_count = len(record.visit_ids)

    def action_create_new_visit(self):
        self.ensure_one()
        return {
            'name': 'Create Visit',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.id,
                'default_doctor_id': self.personal_doctor.id if self.personal_doctor else False,
                'default_status': 'planned',
            }
        }