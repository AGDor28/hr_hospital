import logging

from odoo import models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

CONST_EXP = "Hospital constant example"

class HospitalDoctorCategory(models.Model):
    _name = "hr.hospital.doctor.category"
    _description = "Category"
    _order = 'sequence, id'

    def _default_sequence(self):
        last_record = self.search([], order='sequence desc', limit=1)
        if last_record:
            return last_record.sequence + 1
        return 1

    sequence = fields.Integer(string='Sequence', default=_default_sequence)

    name = fields.Char(string='Category Name', required=True)

    _name_unique = models.Constraint(
        definition='UNIQUE(name)',
        message='The name of category must be unique!'
    )

    doctor_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='category_id',
        string='Doctor'
    )