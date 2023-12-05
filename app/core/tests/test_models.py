"""
Tests for model
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "test123123"
        print(get_user_model())
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_superuser(self):
        """Test create super user"""
        user = get_user_model().objects.create_superuser(
            email="Admin@soheil.com",
            password="Admin123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
