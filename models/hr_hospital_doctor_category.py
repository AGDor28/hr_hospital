import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

CONST_EXP = "Hospital constant example"

class HospitalDoctorCategory(models.Model):
    _name = "hr.hospital.doctor.category"
    _description = "Category"
    _order = 'sort_number asc'

    name = fields.Char(string='Category Name', required=True)

    sort_number = fields.Integer(string='Sort Number', required=True, default=0)

    @api.constrains('name')
    def _check_name_uniq(self):
        for obj in self:
            if self.search([('name', '=', obj.name), ('id', '!=', obj.id)]):
                raise ValidationError('The name of category must be unique!')

    doctor_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='category_id',
        string='Doctor'
    )