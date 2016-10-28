from __future__ import unicode_literals
from django.utils.six import text_type
from django.db.models import Q
from django.utils.html import escape
from choicemaster.models import Subject, Topic
from ajax_select import LookupChannel
import ajax_select


class SubjectLookup(LookupChannel):

    model = Subject

    def get_query(self, q, request):
        return Subject.objects.filter(Q(name__icontains=q) | Q(email__istartswith=q)).order_by('subject_title')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return "%s<div><i>%s</i></div>" % (escape(obj.name), escape(obj.email))
        # return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return "%s<div><i>%s</i></div>" % (escape(obj.name), escape(obj.email))


class TopicLookup(LookupChannel):

    model = Topic

    def get_query(self, q, request):
        return Topic.objects.filter(name__icontains=q).order_by('topic_name')

    def get_result(self, obj):
        return text_type(obj)

    def format_match(self, obj):
        return self.format_item_display(obj)

    def format_item_display(self, obj):
        return "%s<div><i>%s</i></div>" % (escape(obj.name), escape(obj.url))