from django.contrib import admin

from .models import *


admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(Answer)
admin.site.register(Report)


''' Modelos Inline '''

class AnswerInline(admin.TabularInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
    ]