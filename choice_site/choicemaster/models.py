from __future__ import unicode_literals

from django.db import models


class Subject(models.Model):
    subject_title = models.CharField(max_length=40)
    subject_description = models.CharField(max_length=200)


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic_title = models.CharField(max_length=40)
    topic_description = models.CharField(max_length=200)


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    right_answer_id = models.IntegerField()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    exam = models.ManyToManyField(Exam)
    answer_text = models.CharField(max_length=200)


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
    report_state = models.CharField(max_length=2, choices=STATE_CHOICES, default=NOT_EVALUATED)
    report_description = models.CharField(max_length=200)


class Exam(models.Model):
    exam_quantity_questions = models.IntegerField(default=0)
    exam_result = models.IntegerField(default=0)
    exam_timer = models.IntegerField(default=60)
