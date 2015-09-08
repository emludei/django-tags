from django.contrib import admin

from tags.models import Tag, TaggedItem

class TaggedItemInline(admin.TabularInline):
    model = TaggedItem
    extra = 0


class TagAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Tag info', {'fields': ['name', 'slug']}),
    ]

    inlines = [
        TaggedItemInline,
    ]

    list_display = ['name', 'slug']
    ordering = ['name', 'slug']
    search_fields =['name']


admin.site.register(Tag, TagAdmin)
