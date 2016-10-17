from django.test import TestCase, Client
from django.contrib.auth.models import User

# Create your tests here.

class UserTestCase(TestCase):
	def setUp(self):
		user = User.objects.create(username='testuser')
		user.set_password('12345')
		user.save()

		
	def test_user_can_login(self):
		c = Client()
		logged_in = c.login(username='testuser', password='12345')
		self.assertTrue(logged_in)
		c.logout()


class Client():
	
	def test_login_view(self):
		c = Client()
		response = c.get('/accounts/login')
		self.assertEqual(response.status_code, 200)


	def test_index_view(self):
		c = Client()
		logged_in = c.login(username='smarro', password='12345')
		response = c.get('/home/')
		self.assertEqual(response.status_code, 200)

	def test_logout_view(self):
		c = Client()
		logged_in = c.login(username='smarro', password='12345')
		response = c.get('/accounts/logout')
		self.assertEqual(response.status_code, 200)		