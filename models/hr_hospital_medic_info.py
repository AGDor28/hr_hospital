import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class HospitalMedicInfo(models.AbstractModel):
    """An abstract ledger managing foundational anatomical and physiological metrics.

    This class contains shared fields (such as blood typing, gender identification,
    and birth dates) that are universally inherited by active human profiles within
    the hospital, including both `hr.hospital.doctor` and `hr.hospital.patient`.
    """
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
        """Dynamically computes exact current age in years relative to the current date.

        Uses accurate calendar calculation logic to handle varying month lengths
        and leap years. If no birth date is registered, sets age to 0.
        """
        today = fields.Date.today()
        for obj in self:
            if obj.birthday:
                d_birth = fields.Date.from_string(obj.birthday)
                obj.age = relativedelta(today, d_birth).years
            else:
                obj.age = 0
