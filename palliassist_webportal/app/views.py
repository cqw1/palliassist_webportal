from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

# Create your views here.

def index(request):
    #return HttpResponse("Hello, world. You're at the index")
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    context = {
        'title': 'Home Page',
        'year' : datetime.now().year,
    }

    return render(request, 'app/index.html', context)

