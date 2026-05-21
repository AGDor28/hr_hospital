from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import common


class TestHospitalVisit(common.TransactionCase):
    """Test suite dedicated to validating the life cycle and restrictions of patient visits."""

    @classmethod
    def setUpClass(cls):
        """Sets up baseline environment data specifically tailored for visit operations."""
        super().setUpClass()

        cls.user_doctor_1 = cls.env['res.users'].create({
            'name': 'Marc Demo',
            'email': 'mark.brown23@example.com',
            'create_date': '2015-11-12 00:00:00',
            'login': 'demo_1',
            'password': 'demo_1',
        })

        cls.user_doctor_2 = cls.env['res.users'].create({
            'name': 'Dr. Eric Foreman',
            'email': 'foreman@example.com',
            'create_date': '2015-11-12 00:00:00',
            'login': 'demo_2',
            'password': 'demo_2',
        })

        cls.user_patient = cls.env['res.users'].create({
            'name': 'John',
            'email': 'John@example.com',
            'create_date': '2015-11-12 00:00:00',
            'login': 'demo_3',
            'password': 'demo_3',
        })

        cls.doctor_primary = cls.env['hr.hospital.doctor'].create({
            'user_id': cls.user_doctor_1.id,
            'specialty': 'Diagnostics',
        })
        cls.doctor_secondary = cls.env['hr.hospital.doctor'].create({
            'user_id': cls.user_doctor_2.id,
            'specialty': 'Neurology',
        })
        cls.patient = cls.env['hr.hospital.patient'].create({
            'user_id': cls.user_patient.id,
            'insurance_number': 'INS-999-000',
        })

    def test_01_visit_display_name_generation(self):
        """Validates that _compute_display_name builds the exact combined string format."""
        planned_time = fields.Datetime.to_datetime('2026-05-20 14:00:00')

        visit = self.env['hr.hospital.visit'].create({
            'doctor_id': self.doctor_primary.id,
            'patient_id': self.patient.id,
            'planned_date': planned_time,
            'status': 'planned',
        })

        expected_name = "Marc Demo (John) - 2026-05-20 14:00"
        self.assertEqual(
            visit.display_name,
            expected_name,
            f"The computed display name '{visit.display_name}' does not match expected format."
        )

    def test_02_completed_visit_modification_lock(self):
        """Ensures that changing doctor or dates on a completed visit triggers a ValidationError."""
        visit = self.env['hr.hospital.visit'].create({
            'doctor_id': self.doctor_primary.id,
            'patient_id': self.patient.id,
            'planned_date': fields.Datetime.now(),
            'status': 'planned',
        })

        visit.write({'doctor_id': self.doctor_secondary.id})

        visit.write({'status': 'completed'})

        with self.assertRaises(ValidationError, msg="Allowed modifying the doctor on a completed visit."):
            visit.write({'doctor_id': self.doctor_primary.id})

        with self.assertRaises(ValidationError, msg="Allowed modifying the schedule date on a completed visit."):
            visit.write({'planned_date': fields.Datetime.now()})

    def test_03_completed_visit_deletion_and_archival_lock(self):
        """Verifies strict security rules rejecting erasure or archival of completed interactions."""
        visit = self.env['hr.hospital.visit'].create({
            'doctor_id': self.doctor_primary.id,
            'patient_id': self.patient.id,
            'planned_date': fields.Datetime.now(),
            'status': 'completed',
        })

        with self.assertRaises(UserError, msg="Allowed soft-deleting/archiving a completed visit record."):
            visit.write({'active': False})

        with self.assertRaises(UserError, msg="Allowed hard physical deletion of a completed visit record."):
            visit.unlink()
