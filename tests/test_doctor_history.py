from datetime import date

from odoo.tests.common import TransactionCase


class TestHospitalDoctorHistory(TransactionCase):
    """Test suite for validating patient doctor history constraints and synchronizations."""

    @classmethod
    def setUpClass(cls):
        """Sets up organizational and clinical baselines for history testing."""
        super().setUpClass()

        cls.category_cardio = cls.env['hr.hospital.doctor.category'].create({
            'name': 'Cardio',
        })

        cls.user_doc_1 = cls.env['res.users'].create({
            'name': 'Marc Demo',
            'email': 'mark.brown23@example.com',
            'create_date': '2015-11-12 00:00:00',
            'login': 'demo_1',
            'password': 'demo_1',
        })

        cls.user_doc_2 = cls.env['res.users'].create({
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

        cls.doctor_with_category = cls.env['hr.hospital.doctor'].create({
            'user_id': cls.user_doc_1.id,
            'category_id': cls.category_cardio.id,
        })
        cls.doctor_without_category = cls.env['hr.hospital.doctor'].create({
            'user_id': cls.user_doc_2.id,
            'category_id': False,
        })

        cls.patient = cls.env['hr.hospital.patient'].create({
            'user_id': cls.user_patient.id,
        })

    def test_01_display_name_with_category(self):
        """Validates display_name generation when the doctor has an assigned category."""
        test_date = date(2026, 5, 19)

        history_record = self.env['hr.hospital.doctor.history'].create({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor_with_category.id,
            'assignment_date': test_date,
        })

        expected_name = "Marc Demo" if not hasattr(self.doctor_with_category,
                                                   'name') else self.doctor_with_category.name
        expected_display = f"John - {expected_name} (Cardio) 2026-05-19"

        self.assertEqual(
            history_record.display_name,
            expected_display,
            msg="The display_name format with category does not match the model logic."
        )

    def test_02_display_name_without_category(self):
        """Validates display_name generation when the doctor has no category assigned."""
        test_date = date(2026, 5, 20)

        history_record = self.env['hr.hospital.doctor.history'].create({
            'patient_id': self.patient.id,
            'doctor_id': self.doctor_without_category.id,
            'assignment_date': test_date,
        })

        expected_display = "John - Dr. Eric Foreman  2026-05-20"

        self.assertEqual(
            history_record.display_name,
            expected_display,
            msg="The display_name format without category does not match the model logic (check double spaces)."
        )

    def test_03_patient_personal_doctor_synchronization(self):
        """Ensures that creating a history line automatically updates the patient's personal doctor."""

        if hasattr(self.patient, 'personal_doctor_id'):
            self.assertFalse(self.patient.personal_doctor_id, "Patient should not have a personal doctor initially.")

            self.env['hr.hospital.doctor.history'].create({
                'patient_id': self.patient.id,
                'doctor_id': self.doctor_with_category.id,
                'assignment_date': date(2026, 5, 20),
                'active': True,
            })

            self.assertEqual(
                self.patient.personal_doctor_id.id,
                self.doctor_with_category.id,
                msg="The overridden create method failed to synchronize the doctor into the patient's profile."
            )
