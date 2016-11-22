from itertools import chain

from django.forms.widgets import SelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class CheckboxSelectMultiple(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        """
        Renders the received choices. 
        :param request: SelectMultiple, str, int, list, list
        :return: chain
        """
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<div>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<span><label%s>%s %s</label></span><br>' % (label_for,
                                                                        rendered_cb,
                                                                        option_label))
        output.append(u'</div>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        """
        Process the ID for the label
        :param request: id_
        :return: id_
        """
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_