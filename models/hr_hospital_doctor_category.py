import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

CONST_EXP = "Hospital constant example"

class HospitalDoctorCategory(models.Model):
    """Defines qualification ranks or professional groups for doctors.

    Provides custom ordering metrics using a sequence number, allowing hospital
    administrators to visually sort categories (e.g., Chief Physician, Senior Consultant)
    in lists and kanban boards.
    """
    _name = "hr.hospital.doctor.category"
    _description = "Category"
    _order = 'sequence, id'

    def _default_sequence(self):
        """Computes the next logical sequence number for a new category.

        Looks up the highest existing sequence value in the database and increments
        it by 1 to ensure new items appear at the bottom of sorted lists by default.

        Returns:
        int: The next available sequence integer, defaulting to 1 if no records exist.
        """
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
