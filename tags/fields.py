from django.utils import six
from django.utils.translation import ugettext_lazy as _

try:
    from django.contrib.contenttypes.fields import GenericRelation, GenericRel
except ImportError:
    from django.contrib.contenttypes.generic import GenericRelation, GenericRel

from tags.managers import TagFieldManager
from tags.models import TaggedItem
from tags.forms import TagFieldForm
from tags.utils import parse_tagstring


class TagDescriptor:
    def __init__(self, **kwargs):
        self.manager = kwargs.pop('manager')
        self.rel = kwargs.pop('rel')
        self._kwargs = kwargs

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.manager(instance=instance, model=instance_type, **self._kwargs)

    def __set__(self, instance, value):
        if isinstance(value, six.string_types):
            value = parse_tagstring(value)
        if isinstance(value, list):
            manager = self.__get__(instance)
            manager.set(*value)


class TagField(GenericRelation):
    def __init__(self, to=TaggedItem, **kwargs):

        kwargs['verbose_name'] = kwargs.get('verbose_name', _('Tags'))
        kwargs['help_text'] = kwargs.get('help_text', _('A comma-separated list of tags.'))
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['rel'] = GenericRel(
            self, to,
            related_query_name=kwargs.pop('related_query_name', None),
            limit_choices_to=kwargs.pop('limit_choices_to', None)
        )

        kwargs['null'] = True
        kwargs['editable'] = True
        kwargs['serialize'] = False

        self.manager = kwargs.pop('manager', TagFieldManager)
        self.form_class = kwargs.pop('form_class', TagFieldForm)
        self.object_id_field_name = kwargs.pop('object_id_field', 'object_id')
        self.content_type_field_name = kwargs.pop('content_type_field', 'content_type')
        self.for_concrete_model = kwargs.pop('for_concrete_model', True)

        super(GenericRelation, self).__init__(
            to, to_fields=[],
            from_fields=[self.object_id_field_name], **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super(TagField, self).contribute_to_class(cls, name, **kwargs)
        data = {
            'to': self.rel.to,
            'manager': self.manager,
            'rel': self.rel,
            'object_id_field_name': self.object_id_field_name,
            'content_type_field_name': self.content_type_field_name
        }

        setattr(cls, self.name, TagDescriptor(**data))

    def get_internal_type(self):
        return 'TagField'

    def save_form_data(self, instance, data):
        getattr(instance, self.name).set(*data)

    def formfield(self, **kwargs):
        defaults = {
            'label': self.verbose_name.title(),
            'help_text': self.help_text,
            'required': not self.blank,
        }
        defaults.update(kwargs)
        return self.form_class(**defaults)
