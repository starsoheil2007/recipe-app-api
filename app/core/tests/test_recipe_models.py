from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal


class ReModelTest(TestCase):

    def test_create_recipe(self):
        """Create user"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe",
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe decrption',
        )
        self.assertEqual(str(recipe), recipe.title)
