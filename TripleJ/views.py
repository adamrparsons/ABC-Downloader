from django.shortcuts import render, HttpResponse

from django.http import FileResponse
from .download_class import ABCDownloader
from .models import FileRequest

# Delete older requests
import pytz
import shutil
from django.utils import timezone
from datetime import timedelta

def get_file(request):
    
    if request.method == "POST":
        delete_old_reqs()
        url = request.POST["url"]
        file_request = FileRequest.objects.create(
            ip_address = get_client_ip(request),
            request = url,
            directory = None
        )

        downloader = ABCDownloader(pool_size=10)
        filename, dir, pretty_name = downloader.run(url)
        file_request.directory = dir
        file_request.save()
        response = FileResponse(open(filename, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % pretty_name
        return response

    elif request.method == "GET":
        return render(request, template_name="index.html")
    
    else:
        print(request.method)


def delete_old_reqs():
    '''
    When someone requests a file, remove the old ones
    Why is this a hook instead of a cronjob / celery unit?
    I wanted to keep this super simple and run within a single daemon. Fight me. Wordpress does this too

    Deletes the working directory for any requests older than -days-
    '''
    days=1
    for fr in FileRequest.objects.filter(datetime__lte=timezone.now()-timedelta(days=days)):
        try:
            shutil.rmtree(fr.directory)
        except:
            '''
            Bad requests happen sometimes
            '''
            pass


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip