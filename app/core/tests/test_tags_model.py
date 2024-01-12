"""
Test model
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_user(email='user@exapmle.com', password='testpass123'):
    """Create test"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTest(TestCase):

    def test_create_tage(self):
        """
        Create tag
        :return:
        """
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)
