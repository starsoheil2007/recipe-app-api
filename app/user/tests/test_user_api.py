"""
Test for user apis.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test public apis"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Test Create User"""
        payload = {
            'email': 'test@exapmle.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn(payload['password'], res.data)

    def test_user_with_email_exist_error(self):
        """Test"""
        payload = {
            'email': 'test@exapmle.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """Test password short"""
        payload = {
            'email': 'test@exapmle.com',
            'password': 'pw',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test for create token"""
        user = {
            'email': 'test@exapmle.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**user)
        payload = {
            'email': 'test@exapmle.com',
            'password': 'testpass123'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """User not login test"""

        user = {
            'email': 'test@exapmle.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**user)
        payload = {
            'password': 'testpass526',
            'name': 'Test Name'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test fo blank password"""
        payload = {
            'password': '',
            'name': 'Test Name'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test user with token"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123455',
            name='Test name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test profile"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allowed(self):
        """Test post method"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        """Test updated user"""
        payload = {'name': 'update me', 'password': 'jhjdsfjdshfjds'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
