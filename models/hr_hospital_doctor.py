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

    intern_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='mentor_id',
        string='Interns'
    )

    mentor_specialty = fields.Char(
        related='mentor_id.specialty',
        string='Mentor Specialty',
        readonly=True
    )

    mentor_phone = fields.Char(
        related='mentor_id.phone',
        string='Mentor Phone',
        readonly=True
    )

    mentor_email = fields.Char(
        related='mentor_id.email',
        string='Mentor Email',
        readonly=True
    )

    @api.depends('mentor_id')
    def _compute_is_intern(self):
        for obj in self:
            obj.is_intern = bool(obj.mentor_id)

    @api.constrains('mentor_id')
    def _check_mentor_not_intern(self):
        for obj in self:
            if obj.mentor_id:
                if obj.mentor_id.id == obj.id:
                    raise ValidationError("A doctor cannot be their own mentor!")
                if obj.mentor_id.is_intern:
                    raise ValidationError(
                        f"The selected mentor {obj.mentor_id.name} is an intern. "
                        "Only a doctor who is not an intern can be a mentor!"
                    )

    def action_create_visit(self):
        self.ensure_one()
        return {
            'name': 'New Visit',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_doctor_id': self.id,
                'default_planned_date': fields.Datetime.now(),
            }
        }