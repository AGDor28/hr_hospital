from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestDoctorCategory(TransactionCase):
    """Test suite for the 'hr.hospital.doctor.category' model.

    Contains test cases to verify model constraints, field behaviors,
    and data integrity for doctor categories.
    """

    @classmethod
    def setUpClass(cls):
        """Set up initial test data for the doctor category test suite."""
        super().setUpClass()

        cls.category_cardio = cls.env['hr.hospital.doctor.category'].create({
            'name': 'Кардіолог вищої категорії',
            'sequence': 10,
        })

    def test_category_name_unique(self):
        """Verify that the SQL constraint UNIQUE(name) prevents duplicate category names."""

        self.assertTrue(self.category_cardio)

        with self.assertRaises(IntegrityError, msg="База даних повинна викинути помилку при спробі створити дублікат назви"):
            with mute_logger('odoo.sql_db'):
                self.env['hr.hospital.doctor.category'].create({
                    'name': 'Кардіолог вищої категорії',
                    'sequence': 20,
                })
