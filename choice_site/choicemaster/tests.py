from django.test import TestCase, Client
from django.contrib.auth.models import User

# Create your tests here.


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.save()
        self.c = Client()
        self.logged_in = self.c.login(username='testuser', password='12345')

    def test_user_can_login(self):
        self.assertTrue(self.logged_in)

    def test_login_view(self):
        self.c.logout()
        response = self.c.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.logged_in = self.c.login(username='testuser', password='12345')

    def test_index_view(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        response = self.c.get('/accounts/logout/')
        self.assertEqual(response.status_code, 200)
    
    def test_signup_view(self):
        self.c.logout()
        response = self.c.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)