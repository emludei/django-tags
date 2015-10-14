from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey

from tags.utils import slugify


class Tag(models.Model):
    name = models.CharField(verbose_name=_('Tag name'), max_length=40, unique=True)
    slug = models.SlugField(verbose_name=_('Tag slug'), max_length=40, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name.capitalize()


class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('tag', 'content_type', 'object_id')

    @classmethod
    def get_tag_model(cls):
        return cls.tag.field.rel.to

    @classmethod
    def get_tag_related_name(cls):
        return cls.tag.field.rel.related_name or cls.tag.field.rel.name

    @classmethod
    def tags_for_obj(cls, content_type, object_id, **filters):
        filters = filters or {}
        filters.update({
            '%s__content_type' % cls.get_tag_related_name(): content_type,
            '%s__object_id' % cls.get_tag_related_name(): object_id
        })

        return cls.get_tag_model().objects.filter(**filters)

    def __str__(self):
        args = {
            'model': self.obj._meta.model.__name__,
            'obj_id': self.object_id,
            'tag_name': self.tag.name,
        }

        return 'model - {model}, object id - {obj_id}, tag - {tag_name}'.format(**args)
