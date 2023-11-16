from django.contrib import admin
from.models import Document, Comment

# Register your models here.


class DocumentManager(admin.ModelAdmin):
    list_display = ('doc_name', 'date_created', 'size')


admin.site.register(Document, DocumentManager)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'document', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'roll_no', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
