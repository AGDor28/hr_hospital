import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'

    _inherit = ['hr.hospital.medic.info']

    _inherits = {'res.users': 'user_id'}

    specialty = fields.Char(string='Specialty')

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Doctor',
        required=True,
        ondelete='cascade'
    )

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Mentor',

    )

    visit_ids = fields.One2many(
        comodel_name='hr.hospital.visit',
        inverse_name='doctor_id',
        string='Visits'
    )

    category_id = fields.Many2one(
        comodel_name='hr.hospital.doctor.category',
        string='Category'
    )

    is_intern = fields.Boolean(
        compute='_compute_is_intern',
        string='Is Intern',
        store=True,
    )

    @api.depends('mentor_id')
    def _compute_is_intern(self):
        for obj in self:
            if obj.mentor_id:
                obj.is_intern = True
            else:
                obj.is_intern = False

    @api.constrains('mentor_id')
    def _check_mentor_not_intern(self):
        for obj in self:
            if obj.mentor_id and obj.mentor_id.is_intern:
                obj.mentor_id = False
                raise ValidationError(
                    f"The selected mentor {obj.mentor_id.name} is an intern. "
                    "Only a doctor who is not an intern can be a mentor!"
                )