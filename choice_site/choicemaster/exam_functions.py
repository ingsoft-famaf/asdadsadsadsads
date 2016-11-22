from choicemaster import models
import json
import random


def get_question(exam_id):
    """
    Get a question from the list of questions of the given topics. Consider the
    cases when the exam has the algorithm mode on and off as separate.
    :param request: Exam
    :return: Question
    """
    exam = models.Exam.objects.get(pk=exam_id)
    questions = exam.questions.all()
    questions_dict = dict()
    questions_used = exam.questions.all()
    questions_used_dict = dict()

    for q in questions:
        questions_dict[str(q.id)] = q

    for q in questions_used:
        questions_used_dict[str(q.id)] = q

    if exam.exam_algorithm:
        # in case the exam was configured with a based-on-errors algorithm
        # then pick a random question from the ones the user answered
        # incorrectly among the previous questions in the exam

        mistakes = get_mistakes(exam_id)
        topic_id = max(mistakes, key=mistakes.get)
        questions_topic = models.Question.objects.filter(topic=topic_id,
                                                         available=True)

        try:
            question = questions_dict[random.choice(questions_dict.keys())]
            exam.questions_used.add(question)
            exam.questions.remove(question)
        except IndexError:
            question = questions_dict[random.choice(questions_dict.keys())]
            exam.questions_used.add(question)
            exam.questions.remove(question)

    else:
        # otherwise just pick a random question from the ones left to answer
        # in the exam
        index_t = random.choice(questions_dict.keys())
        question = questions_dict[index_t]
        exam.questions_used.add(question)
        exam.questions.remove(question)

    return question


def get_mistakes(exam_id):
    """
    Get mistakes associated to a given exam.
    :param request: Exam
    :return: list
    """
    exam = models.Exam.objects.get(pk=exam_id)
    jsonDec = json.decoder.JSONDecoder()
    mistakes = jsonDec.decode(exam.mistakes)

    return mistakes
