import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'

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

    visit_ids = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='Visits'
    )