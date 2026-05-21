from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHospitalDoctor(TransactionCase):
    """Test suite for validating doctor profiles, mentorship restrictions, and intern logic."""

    @classmethod
    def setUpClass(cls):
        """Sets up master and transactional data for doctor test constraints."""
        super().setUpClass()

        cls.category_high = cls.env['hr.hospital.doctor.category'].create({
            'name': 'High Qualification',
            'sequence': 10,
        })
        cls.category_intern = cls.env['hr.hospital.doctor.category'].create({
            'name': 'Intern1',
            'sequence': 30,
        })

        cls.doctor_mentor = cls.env['hr.hospital.doctor'].create({
            'name': 'Marc Demo',
            'email': 'mark.brown23@example.com',
            'create_date': '2015-11-12 00:00:00',
            'login': 'demo_1',
            'password': 'demo_1',
            'category_id': cls.category_high.id,
        })

        cls.doctor_intern_1 = cls.env['hr.hospital.doctor'].create({
            'name': 'Dr. Eric Foreman',
            'email': 'foreman@example.com',
            'create_date': '2015-11-12 00:00:00',
            'login': 'demo_2',
            'password': 'demo_2',
            'category_id': cls.category_intern.id,
            'mentor_id': cls.doctor_mentor.id,
        })

    def test_01_doctor_mentor_constraints(self):
        """Test suite for validating doctor profiles, mentorship restrictions, and intern logic."""

        self.assertTrue(self.doctor_intern_1.is_intern, msg="Doctor with an assigned mentor must be flagged as an intern.")
        self.assertFalse(self.doctor_mentor.is_intern, msg="Doctor without a mentor must not be flagged as an intern")

        self_mentor_doctor = self.env['hr.hospital.doctor'].create({
            'name': 'Dr. Independent',
            'login': 'independent_doc_test',
            'email': 'independent@hospital.com',
        })

        with self.assertRaises(ValidationError, msg="Allowed a doctor to become their own mentor."):
            self_mentor_doctor.write({'mentor_id': self_mentor_doctor.id})

        with self.assertRaises(ValidationError, msg="Allowed an intern to act as a mentor for another doctor."):
            self.env['hr.hospital.doctor'].create({
                'name': 'New Intern',
                'login': 'new_intern_test',
                'email': 'new_intern@hospital.com',
                'mentor_id': self.doctor_intern_1.id,
            })
