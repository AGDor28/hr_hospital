import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

CONST_EXP = "Hospital constant example"

class HospitalDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Disease"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(string='Disease Name', required=True)

    description = fields.Text(string='Description')

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Patient'
    )

    parent_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Parent Disease',
        index=True,
        ondelete='cascade',
    )

    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        comodel_name='hr.hospital.disease',
        inverse_name='parent_id',
        string='Child Disease',
    )

    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
        recursive=True
    )

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id and self.parent_id.id == self.id.origin:
            return {
                    'warning': {
                        'title': "Warning",
                        'message': "You cannot create recursive hierarchy"
                    }
                }
        return None

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError("Error! You cannot create recursive hierarchy."
            )

    @api.depends('name', 'parent_id')
    def _compute_display_name(self):
        for obj in self:
            if obj.parent_id:
                name = obj.name
                parent = obj.parent_id
                while parent:
                    name = f"{parent.name} / {name}"
                    parent = parent.parent_id
                obj.display_name = name
            else:
                obj.display_name = obj.name
