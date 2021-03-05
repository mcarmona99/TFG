from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# This is the simplest view possible in Django. To call the view, we need to map it to a URL - and for this we need a
# URLconf.
