import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'

    _inherits = {'res.partner': 'partner_id'}

    specialty = fields.Char(string='Specialty')

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Doctor',
        required=True,
        ondelete='cascade'
    )

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Mentor'
    )