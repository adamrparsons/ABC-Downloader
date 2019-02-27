from django.contrib import admin
from .models import FileRequest

class FileRequestAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'ip_address', 'request', 'directory')

admin.site.register(FileRequest, FileRequestAdmin)