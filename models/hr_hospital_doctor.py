import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class HospitalDoctor(models.Model):
    """Represents a medical doctor within the hospital system.

    This model manages doctor profiles, specialized medical fields, mentor-intern
    relationships, and coordinates scheduled patient visits. It inherits core
    identity management from Odoo's built-in user system.
    """
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

    color = fields.Integer(
        string='Color Index'
    )

    intern_names_list = fields.Char(
        compute='_compute_intern_names_list',
        string='Intern Names List'
    )

    @api.depends('intern_ids.name')
    def _compute_intern_names_list(self):
        """Generates a comma-separated string listing all assigned interns' names.

        Used primarily for clean visual tracking in kanban or list views without
        rendering an entire sub-grid.
        """
        for doc in self:
            doc.intern_names_list = ", ".join(doc.intern_ids.mapped('name'))

    @api.depends('mentor_id')
    def _compute_is_intern(self):
        """Determines if a doctor is an intern based on the presence of a mentor.

        If a doctor has an assigned mentor, they are automatically categorized
        as an intern.
        """
        for obj in self:
            obj.is_intern = bool(obj.mentor_id)

    @api.constrains('mentor_id')
    def _check_mentor_not_intern(self):
        """Validates that mentorship rules are legally met.

        Prevents circular/self-mentorship and restricts interns from acting as
        mentors to other doctors.

        Raises:
        ValidationError: If a doctor attempts to mentor themselves, or if the
        selected mentor is already an intern.
        """
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
        """Opens a wizard popup to schedule a new visit for this doctor.

        Returns:
        dict: An ir.actions.act_window action dictionary displaying the
        visit form view pre-populated with the current doctor and time.
        """
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
