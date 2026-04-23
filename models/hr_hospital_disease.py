import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

CONST_EXP = "Hospital constant example"

class HospitalDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Disease"

    name = fields.Char(string='Disease Name', required=True)

    description = fields.Text(string='Description')

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Patient'
    )