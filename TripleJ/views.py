from django.shortcuts import render, HttpResponse

from django.http import FileResponse
from .download_class import ABCDownloader
from .models import FileRequest

def get_file(request):
    
    if request.method == "POST":
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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip