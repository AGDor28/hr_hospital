import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class HospitalVisit(models.Model):
    _name = "hr.hospital.visit"
    _description = "Patient Visit"

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True
    )

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True
    )

    status = fields.Selection([
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ],
        string='Status',
        default='planned',
        required=True
    )

    planned_date = fields.Datetime(
        string='Planned Date',
        required=True,
        help="Scheduled time for the visit"
    )

    visit_date = fields.Datetime(
        string='Actual Visit Date',
    )

    summary = fields.Html(string='Summary / Epicrisis')

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Disease'
    )

    active = fields.Boolean(default=True)

    @api.constrains('doctor_id', 'planned_date', 'visit_date', 'status')
    def _check_completed_visit_changes(self):
        for record in self:
            if record._origin.status == 'completed':
                if (record.doctor_id != record._origin.doctor_id or
                        record.planned_date != record._origin.planned_date or
                        record.visit_date != record._origin.visit_date):
                    raise ValidationError(
                        "You cannot modify the Doctor or Dates of a visit that has already been completed."
                    )

    def unlink(self):
        for obj in self:
            if obj.status == 'completed':
                raise UserError("You cannot delete a visit that has already taken place.")
        return super().unlink()

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            for obj in self:
                if obj.status == 'completed':
                    raise UserError("You cannot archive a visit that has already taken place.")
        return super().write(vals)

    @api.depends('doctor_id', 'planned_date', 'patient_id')
    def _compute_display_name(self):
        for record in self:
            name = f"{record.doctor_id.name}"
            if record.patient_id:
                name += f" ({record.patient_id.name})"
            if record.planned_date:
                name += f" - {record.planned_date.strftime('%Y-%m-%d %H:%M')}"
            record.display_name = name

    def action_view_similar_disease_visits(self):
        self.ensure_one()
        return {
            'name': 'Visits with Same Disease',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form',
            'domain': [('disease_id', '=', self.disease_id.id)],
            'context': {'default_disease_id': self.disease_id.id},
            'target': 'current',
        }
