from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    subject_title = models.CharField(max_length=40)
    subject_description = models.CharField(max_length=200)
    subject_department = models.CharField(max_length=50)

    """
    Method to show the correct object name in the admin interface.
    """
    def __unicode__(self):
        return self.subject_title


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic_title = models.CharField(max_length=40)
    topic_description = models.CharField(max_length=200)

    """
    Method to show the correct object name in the admin interface.
    """
    def __unicode__(self):
        return self.topic_title


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)

    """
    Method to show the correct object name in the admin interface.
    """
    def __unicode__(self):
        return self.question_text


class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default=0)
    exam_quantity_questions = models.IntegerField(default=0)
    exam_timer = models.IntegerField(default=60)
    exam_algorithm = models.CharField(max_length=200, default=0)
    exam_result = models.IntegerField(default=0)
    topic = models.ManyToManyField(Topic)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    """
    Method to show the correct object name in the admin interface.
    """
    def __unicode__(self):
        return self.answer_text


class QuestionSnapshot(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=0)
    question_text = models.CharField(max_length=200)
    chosen_answer = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)
    choice_correct = models.BooleanField(default=True)


class Report(models.Model):
    NOT_EVALUATED = 'NE'
    IN_EVALUATION = 'IE'
    EVALUATED = 'E'
    STATE_CHOICES = (
        (NOT_EVALUATED, 'Not evaluated'),
        (IN_EVALUATION, 'In evaluation'),
        (EVALUATED, 'Evaluated'),
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    report_state = models.CharField(max_length=2, choices=STATE_CHOICES,
                                    default=NOT_EVALUATED)
    report_description = models.CharField(max_length=200)

    """
    Method to show the correct object name in the admin interface.
    """
    def __unicode__(self):
        return self.question.question_text
