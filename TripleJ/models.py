from django.db import models

class FileRequest(models.Model):
    datetime = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request = models.URLField()
    directory = models.CharField(max_length=200, null=True, blank=True)
