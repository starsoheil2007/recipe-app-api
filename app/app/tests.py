"""
Simple tests
"""

from django.test import SimpleTestCase

from app import calc


class CalcTest(SimpleTestCase):
    """Test the calc"""

    def test_add_number(self):
        """Test adding number"""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)
