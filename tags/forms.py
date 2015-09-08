from django import forms
from django.utils import six
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from tags.utils import parse_tagstring, edit_string_for_tag_names


class TagWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, six.string_types):
            value = edit_string_for_tag_names(value.names())
        attrs['class'] = 'vTextField'
        
        return super(TagWidget, self).render(name, value, attrs)


class TagFieldForm(forms.CharField):
    widget = TagWidget

    def clean(self, value):
        value = super(TagFieldForm, self).clean(value)
        msg = _('Please provide a comma-separated list of tags.')

        try:
            tags = parse_tagstring(value)            
        except ValueError:
            raise forms.ValidationError(msg)

        if self.required and not tags:
            froms.ValidationError(msg)
        
        return tags
