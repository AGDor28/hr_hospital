import logging

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class HospitalMedicInfo(models.AbstractModel):
    _name = 'hr.hospital.medic.info'
    _description = 'Abstract Medical Information'

    blood_group = fields.Selection([
        ('o+', 'O(I) Rh+'),
        ('o-', 'O(I) Rh-'),
        ('a+', 'A(II) Rh+'),
        ('a-', 'A(II) Rh-'),
        ('b+', 'B(III) Rh+'),
        ('b-', 'B(III) Rh-'),
        ('ab+', 'AB(IV) Rh+'),
        ('ab-', 'AB(IV) Rh-'),
    ], string='Blood Group')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender')

    birthday = fields.Date(string='Date of Birth')

    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=False
    )

    @api.depends('birthday')
    def _compute_age(self):
        today = fields.Date.today()
        for obj in self:
            if obj.birthday:
                d_birth = fields.Date.from_string(obj.birthday)
                obj.age = relativedelta(today, d_birth).years
            else:
                obj.age = 0
