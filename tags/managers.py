from django.db import models, router, transaction
from django.utils import six
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import create_generic_related_manager


class TagFieldManager(models.Manager):
    def __init__(self, to, instance, model, object_id_field_name, content_type_field_name):
        self.to = to
        self.instance = instance
        self.model = model
        self.tag_model = self.to.get_tag_model()
        self.object_id_field_name = object_id_field_name
        self.content_type_field_name = content_type_field_name
        self.content_type = ContentType.objects.get_for_model(self.model)
        
        self.filters = {
            self.content_type_field_name: self.content_type,
            self.object_id_field_name: self.instance.pk
        }

        self._db = router.db_for_write(self.model, instance=self.instance)

    def get_queryset(self, **filters):
        return self.to.tags_for_obj(self.content_type, self.instance.pk, **filters)

    def add(self, *tags):
        tag_objs, str_tags = self._split_tags_on_objs_and_str(*tags)
        tag_objs.update(self._get_or_create_tag_objs(str_tags))

        for tag in tag_objs:
            self.to.objects.get_or_create(tag=tag, **self.filters)

    def set(self, *tags, clear=False):
        with transaction.atomic(using=self._db, savepoint=False):
            if clear:
                self.clear()
                self.add(*tags)
            else:
                tag_objs, str_tags = self._split_tags_on_objs_and_str(*tags)
                tag_objs.update(self._get_or_create_tag_objs(str_tags))
                
                old_objs = list(self.get_queryset())
                new_objs = []

                for tag in tag_objs:
                    if tag in old_objs:
                        old_objs.remove(tag)
                    else:
                        new_objs.append(tag)

                self.remove(*old_objs)
                self.add(*new_objs)
    
    def remove(self, *tags):
        tag_objs, str_tags = self._split_tags_on_objs_and_str(*tags)

        if str_tags:
            self.to.objects.filter(
                tag__name__in=str_tags,
                **self.filters
            ).delete()

        if tag_objs:
            self.to.objects.filter(
                tag__in=tag_objs,
                **self.filters
            ).delete()

    def clear(self):
        self.to.objects.filter(
            **self.filters
        ).delete()

    def names(self):
        return self.get_queryset().values_list('name', flat=True)

    def slugs(self):
        return self.get_queryset().values_list('slug', flat=True)

    def _split_tags_on_objs_and_str(self, *tags):
        str_tags = set()
        tag_objs = set()

        for tag in tags:
            if isinstance(tag, self.tag_model):
                tag_objs.add(tag)
            elif isinstance(tag, six.string_types):
                str_tags.add(tag)
            else:
                ValueError('Invalid type of element {0} ({1}).'.format(tag, type(tag)))

        return tag_objs, str_tags

    def _get_or_create_tag_objs(self, str_tags):
        tag_objs = set()
        existing_tags = self.tag_model.objects.filter(name__in=str_tags)
        tags_to_create = str_tags - {tag.name for tag in existing_tags}

        tag_objs.update(existing_tags)

        for tag in tags_to_create:
            tag_objs.add(self.tag_model.objects.create(name=tag))

        return tag_objs
