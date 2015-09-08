from django import template
from django.contrib.contenttypes.models import ContentType

from tags.models import TaggedItem


register = template.Library()
