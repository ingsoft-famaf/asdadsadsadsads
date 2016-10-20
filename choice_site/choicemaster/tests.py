from django.test import TestCase, Client
from django.contrib.auth.models import User


class UserTestCase(TestCase):

    def setUp(self):
        """
        Create a new user and verify that the login function works properly
        """
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.save()
        self.c = Client()
        self.logged_in = self.c.login(username='testuser', password='12345')

    def test_user_can_login(self):
        """
        Check that the user entity has its logged_in state equal to TRUE,
        since it just logged in
        """
        self.assertTrue(self.logged_in)

    def test_login_view(self):
        """i
        Logout from an account, check that the login view is displayed
        successfully, and login with a username and a password
        """
        self.c.logout()
        response = self.c.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.logged_in = self.c.login(username='testuser', password='12345')

    def test_index_view(self):
        """
        Make sure that our homepage returns an HTTP 200 status code for a
        successful HTTP request
        """
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """
        Test that our website returns an HTTP 200 status after a successful
        logout request 
        """
        response = self.c.get('/accounts/logout/')
        self.assertEqual(response.status_code, 200)

    def test_signup_view(self):
        """
        Check that our website returns an HTTP 200 status after a successful
        signup request
        """
        self.c.logout()
        response = self.c.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

    def test_password_wrong(self):
        c = Client()
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com', 'password1': '1234567a',
                                               'password2': '12345678b', 'username': 'prueba'})

        self.assertEquals(response.status_code, 200)
        assert("You must type the same password each time." in response.content)

    def test_short_password(self):
        c = Client()
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com', 'password1': '123456',
                                                'password2': '123456', 'username': 'prueba'})
        self.assertEquals(response.status_code, 200)
        assert ("This password is too short. It must contain at least 8 characters." in response.content)

    def test_password_without_character(self):
        c = Client()
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com', 'password1': '123456789',
                                                'password2': '123456789', 'username': 'prueba'})
        self.assertEquals(response.status_code, 200)
        assert ("This password is entirely numeric." in response.content)

    def test_Username_already_registered(self):
        c = Client()
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com', 'password1': '123456789a',
                                                'password2': '123456789a', 'username': 'prueba'})
        self.assertEquals(response.status_code, 200)
        response = c.post('/accounts/signup/', {'email': 'prueba1@gmail.com', 'password1': '123456789a',
                                                'password2': '123456789a', 'username': 'prueba'})
        self.assertEquals(response.status_code, 302)
        assert ("A user with that username already exists." in response.content)

    def test_email_already_registered(self):
        c = Client()
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com', 'password1': '123456789a',
                                                'password2': '123456789a', 'username': 'prueba'})
        self.assertEquals(response.status_code, 200)
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com', 'password1': '123456789a',
                                                'password2': '123456789a', 'username': 'prueba1'})
        self.assertEquals(response.status_code, 302)
        assert ("A user is already registered with this e-mail address." in response.content)