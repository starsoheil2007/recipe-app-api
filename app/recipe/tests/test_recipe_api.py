"""
Test for recipe apis
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
import tempfile
import os
from PIL import Image

from core.models import (
    Recipe, Tag
)
from recipe.serializer import (
    RecipeSerializer,
    RecipeDetailSerializer
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create recipe url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    """
    Create recipe
    :param user:
    :param params:
    :return:
    """
    defaults = {
        'title': 'smaple recipe',
        'time_minutes': 25,
        'price': Decimal('5.25'),
        'description': 'saasf',
        'link': 'http://google.com'
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user,
                                   **defaults)
    return recipe


def create_user(**params):
    """Create and return"""
    return get_user_model().objects.create_user(**params)


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


class PublicRecipeAPITest(TestCase):
    """test unauthenticated user"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test authenticated api request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@exqample.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test get list"""
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        respices = Recipe.objects.all().order_by("-id")

        serilizer = RecipeSerializer(respices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serilizer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipe"""
        other_user = create_user(
            email='other@example.com',
            password='password123'
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        respies = Recipe.objects.filter(user=self.user)
        serilizer = RecipeSerializer(respies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serilizer.data)

    def test_get_recipe_detail(self):
        """Test get recipe"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serialzer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serialzer.data)

    def test_create_recipe(self):
        """Test create"""
        payload = {
            'title': 'smaple recipe 2',
            'time_minutes': 25,
            'price': Decimal('5.25'),
            'description': 'saasf',
            'link': 'http://google.com'
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Update"""

        recipe = create_recipe(
            user=self.user,
            title="Sample",
            link="httl"
        )
        payload = {'title': 'new recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, recipe.link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Full update"""
        recipe = create_recipe(
            user=self.user,
            title="Sample",
            link="httl",
            description="asdsafsa safasf"
        )
        payload = {
            'title': 'new recipe title',
            'link': "httl",
            'description': "asdsafsa safasf",
            'time_minutes': 25,
            'price': Decimal('2.50')
        }

        url = detail_url(recipe.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_return_error(self):
        """"""
        other_user = create_user(
            email='other@example.com',
            password='password123'
        )
        recipe = create_recipe(
            user=self.user,
            title="Sample",
            link="httl",
            description="asdsafsa safasf"
        )
        payload = {'user': other_user.id}

        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_item(self):
        recipe = create_recipe(
            user=self.user,
            title="Sample",
            link="httl",
            description="asdsafsa safasf"
        )
        url = detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Trye to delete other user recipe"""
        other_user = create_user(
            email='other@example.com',
            password='password123'
        )
        recipe = create_recipe(
            user=other_user,
            title="Sample",
            link="httl",
            description="asdsafsa safasf"
        )

        url = detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)

    def test_create_tag_on_update(self):
        """Test updating a recipe with patch"""
        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Update Existing tag"""
        tag_break = Tag.objects.create(user=self.user, name='breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_break)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_break, recipe.tags.all())

    def test_filter_by_tags(self):
        """Test filtering by recep"""
        r1 = create_recipe(self.user, title='Ths 1')
        r2 = create_recipe(self.user, title='Ths 2')
        tag1 = Tag.objects.create(user=self.user, name='Vigen')
        tag2 = Tag.objects.create(user=self.user, name='Beef')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(self.user, title='Ths 3')
        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPES_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )

        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Invalid image"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'noIMgae'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
