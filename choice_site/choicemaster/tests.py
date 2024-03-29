from django.test import TestCase, Client
from django.contrib.auth.models import User
from models import *
import os


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
        self.user_staff = User.objects.create_superuser(username='teststaff',
                                                        email='',
                                                        password='123456789a')
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
        logged_in_staff = self.cp.login(username='teststaff',
                                        password='123456789a')
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
        logged_in_staff = self.cp.login(username='teststaff',
                                        password='123456789a')
        response = self.cp.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue("Add subject" in response.content)
        self.assertTrue("Add topic" in response.content)
        self.assertTrue("Add questions" in response.content)

    def test_report(self):
        """
        Check existing reports. Creates a report in case there is none in the
        app report's database.
        """
        self.cp.logout()
        logged_in_staff = self.cp.login(username='teststaff',
                                        password='123456789a')
        response = self.cp.get('/')
        self.assertEquals(response.status_code, 200)
        if len(Report.objects.all()) == 0:
            # Se crea una denuncia.
            self.assertTrue("No complaints" in response.content)

            subject = Subject.objects.create(subject_title="Materia",
                                             subject_description="Comentario",
                                             subject_department="Famaf")

            topic = Topic.objects.create(subject=subject,
                                         topic_title="un tema",
                                         topic_description="Una descripcion")

            question = Question.objects.create(topic=topic,
                                               question_text="Una pregunta")

            report = Report.objects.create(report_state="NE",
                                           report_description="Esto es una"
                                                              "prueba",
                                           question=question)
            response = self.cp.get('/')

        self.assertTrue("Reported questions" in response.content)
        response = self.cp.get('/report/')
        self.assertEquals(response.status_code, 200)


class TestQuestionModel(TestCase):

    def setUp(self):
        self.subj = Subject.objects.create(
            subject_title='Subject X',
            subject_description='Subject X description',
            subject_department='Tests Department')

        self.topc = Topic.objects.create(
            subject=self.subj,
            topic_title='Topic X',
            topic_description='Topic X description')

        self.q = Question.objects.create(
            topic=self.topc,
            question_text='Which of the following choices '
            'is the correct answer for Q?')

        self.a1 = Answer.objects.create(question=self.q,
                                        answer_text='Wrong answer',
                                        correct=False)

        self.a2 = Answer.objects.create(question=self.q,
                                        answer_text='Correct answer',
                                        correct=True)

        self.a3 = Answer.objects.create(question=self.q,
                                        answer_text='Wrong answer',
                                        correct=False)

    def test_answers(self):
        answers = Answer.objects.filter(question=self.q)
        correct_a = Answer.objects.get(question=self.q,
                                       correct=True)

        self.assertEqual(answers.count(), 3)
        self.assertEqual(correct_a.answer_text, "Correct answer")

        for answer in answers:
            if answer != correct_a:
                self.assertEqual(answer.correct, False)


class TestExam(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('dga-245vl,')
        self.user.email = 'testmail@test.com'
        self.user.save()
        self.c = Client()
        self.logged_in = self.c.login(
            username='testuser', password='dga-245vl,')

        self.subj = Subject.objects.create(
            subject_title='Subject X',
            subject_description='Subject X description',
            subject_department='Tests Department')

        self.topc = Topic.objects.create(
            subject=self.subj,
            topic_title='Topic X',
            topic_description='Topic X description')

        self.q1 = Question.objects.create(
            topic=self.topc,
            question_text='Which of the following choices '
            'is the correct answer for Q1?')

        self.q1a1 = Answer.objects.create(question=self.q1,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q1a2 = Answer.objects.create(question=self.q1,
                                          answer_text='Correct answer.',
                                          correct=True)

        self.q1a3 = Answer.objects.create(question=self.q1,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q2 = Question.objects.create(
            topic=self.topc,
            question_text='Which of the following choices '
            'is the correct answer for Q2?')

        self.q2a1 = Answer.objects.create(question=self.q2,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q2a2 = Answer.objects.create(question=self.q2,
                                          answer_text='Correct answer.',
                                          correct=True)

        self.q2a3 = Answer.objects.create(question=self.q2,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q3 = Question.objects.create(
            topic=self.topc,
            question_text='Which of the following choices '
            'is the correct answer for Q3?')

        self.q3a1 = Answer.objects.create(question=self.q3,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q3a2 = Answer.objects.create(question=self.q3,
                                          answer_text='Correct answer.',
                                          correct=True)

        self.q3a3 = Answer.objects.create(question=self.q3,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q4 = Question.objects.create(
            topic=self.topc,
            question_text='Which of the following choices '
            'is the correct answer for Q4?')

        self.q4a1 = Answer.objects.create(question=self.q4,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q4a2 = Answer.objects.create(question=self.q4,
                                          answer_text='Correct answer.',
                                          correct=True)

        self.q4a3 = Answer.objects.create(question=self.q4,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q5 = Question.objects.create(
            topic=self.topc,
            question_text='Which of the following choices '
            'is the correct answer for Q5?')

        self.q5a1 = Answer.objects.create(question=self.q5,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.q5a2 = Answer.objects.create(question=self.q5,
                                          answer_text='Correct answer.',
                                          correct=True)

        self.q5a3 = Answer.objects.create(question=self.q5,
                                          answer_text='Wrong answer.',
                                          correct=False)

        self.exam1 = Exam.objects.create(user=self.user,
                                         subject=self.subj,
                                         exam_quantity_questions=5,
                                         exam_timer=10,
                                         exam_algorithm=1)

        self.exam1.topic.add(self.topc)

        self.exam1.questions.add(self.q1)
        self.exam1.questions.add(self.q2)
        self.exam1.questions.add(self.q3)
        self.exam1.questions.add(self.q4)
        self.exam1.questions.add(self.q5)

        self.exam2 = Exam.objects.create(user=self.user,
                                         subject=self.subj,
                                         exam_quantity_questions=2,
                                         exam_timer=10,
                                         exam_algorithm=1)

        self.exam1.topic.add(self.topc)

        self.exam2.questions.add(self.q1)
        self.exam2.questions.add(self.q2)

    def test_exam_subject_correct(self):
        self.assertEqual(self.exam1.subject, self.subj)

    def test_exam_all_questions_in_subject(self):
        exam1_questions = self.exam1.questions.all()
        exam2_questions = self.exam2.questions.all()
        for question in exam1_questions:
            question_subject = question.topic.subject
            self.assertEqual(question_subject, self.subj)
        for question in exam2_questions:
            question_subject = question.topic.subject
            self.assertEqual(question_subject, self.subj)

    def test_exam_all_questions_in_topic(self):
        exam1_questions = self.exam1.questions.all()
        exam2_questions = self.exam2.questions.all()
        for question in exam1_questions:
            self.assertEqual(question.topic, self.topc)
        for question in exam2_questions:
            self.assertEqual(question.topic, self.topc)
