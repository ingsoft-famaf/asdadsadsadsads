from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import *


class UserTestCase(TestCase):
    def setUp(self):
        """
        Create a new user and verify that the login function works properly
        """
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.email = 'testmail@test.com'
        self.user.save()
        self.c = Client()
        self.logged_in = self.c.login(username='testuser', password='12345')

        
        self.user_staff = User.objects.create_superuser(username='teststaff', \
                            email='', password='123456789a')
        self.user_staff.save()
        self.cp = Client()

    def test_user_can_login(self):
        """
        Check that the user entity has its logged_in state equal to TRUE,
        since it just logged in
        """
        self.assertTrue(self.logged_in)

    def test_user_staff_can_login(self):
        """
        Check that the user staff entity has its logged_in state equal to TRUE,
        since it just logged in
        """
        logged_in_staff = self.cp.login(username='teststaff', password= \
                            '123456789a')
        self.assertTrue(logged_in_staff)

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
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com',
                                                'password1': '1234567a',
                                                'password2': '12345678b',
                                                'username': 'prueba'})

        self.assertEquals(response.status_code, 200)
        self.assertTrue("You must type the same password each time."
                        in response.content)

    def test_short_password(self):
        c = Client()
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com',
                                                'password1': '123456',
                                                'password2': '123456',
                                                'username': 'prueba'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("This password is too short. It must contain "
                        "at least 8 characters." in response.content)

    def test_password_without_character(self):
        c = Client()
        response = c.post('/accounts/signup/', {'email': 'prueba@gmail.com',
                                                'password1': '123456789',
                                                'password2': '123456789',
                                                'username': 'prueba'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("This password is entirely numeric."
                        in response.content)

    def test_Username_already_registered(self):
        self.c.logout()
        response = self.c.post('/accounts/signup/', {'email': 'prueba'
                                                              '@gmail.com',
                                                     'password1': '123456789a',
                                                     'password2': '123456789a',
                                                     'username': 'testuser'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("A user with that username already exists."
                        in response.content)

    def test_email_already_registered(self):
        self.c.logout()
        response = self.c.post('/accounts/signup/', {'email': 'testmail@'
                                                              'test.com',
                                                     'password1': '123456789a',
                                                     'password2': '123456789a',
                                                     'username': 'prueba'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue("A user is already registered with this e-mail "
                        "address." in response.content)


    def test_staff_has_special_homepage(self):
        self.cp.logout()
        logged_in_staff = self.cp.login(username='teststaff', password= \
                            '123456789a')
        response = self.cp.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue("Add subject" in response.content)
        self.assertTrue("Add topic" in response.content)
        self.assertTrue("Add questions" in response.content)


class LoadQuestionsTestCase(TestCase):
    def setUp(self):
        """
        Create a new admin user, and test subject and topic in which to test
        different questions files
        """
        self.user_staff = User.objects.create_superuser(username='teststaff', \
                          email='adminstaff@staff.com', password='123456789a')
        self.user_staff.save()

        self.subj1 = Subject.objects.create(
                                subject_title='Test Subject',
                                subject_description='Test subject description',
                                subject_department='Test Department')

        self.topc1 = Topic.objects.create(subject=self.subj1,
                                    topic_title='Test topic',
                                    topic_description='Test topic description')
        self.c = Client()

    def test_question_file_wrong_format(self):
        c = Client()
        response = c.post('add/question/'+ str(self.subj1.id) +'/'
            + str(self.topc1.id) + '/', files={'wrong_format.xml': 
            open('/choicemaster/xml_files/wrong_format.xml', 'rb')})
        self.assertEquals(response.status_code, 500)

    def test_duplicate_question_with_db(self):
        c = Client()
        response = c.post('add/question/'+ str(self.subj1.id) +'/'
            + str(self.topc1.id) + '/', files={'simple_question.xml': 
            open('/xml_files/wrong_format.xml', 'rb')})

        self.assertEquals(response.status_code, 200)

        response = c.post('add/question/'+ str(self.subj1.id) +'/'
            + str(self.topc1.id) + '/', files={'simple_question.xml':
            open('/xml_files/wrong_format.xml', 'rb')})

        self.assertEquals(response.status_code, 500)

    def test_duplicate_question_with_question_file(self):
        c = Client()
        response = c.post('add/question/'+ str(self.subj1.id) +'/'
            + str(self.topc1.id) + '/', files={'/xml_files/duplicate\
            _with_qf.xml': open('/xml_files/wrong_format.xml', 'rb')})
        self.assertEquals(response.status_code, 500)