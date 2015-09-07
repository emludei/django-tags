from django.views.generic import ListView
from django.contrib.contenttypes.models import ContentType

from tags.models import TaggedItem


class TaggedListObjects(ListView):
    def get_queryset(self):
        id_list = TaggedItem.objects.filter(
            tag__slug=self.kwargs['slug'],
            content_type=ContentType.objects.get_for_model(self.model)
        ).values_list('object_id', flat=True)

        return self.model.objects.filter(id__in=id_list)

    def dispatch(self, request, *args, **kwargs):
        self.model = kwargs.get('model', None)
        self.template_name = kwargs.get('template_name', 'tagged_list_objects.html')
        self.context_object_name = kwargs.get('context_object_name', 'tagged_list_objects')
        self.paginate_by = kwargs.get('paginate_by', 10)

        return super(TaggedListObjects, self).dispatch(request, *args, **kwargs)