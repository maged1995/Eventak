from django.http import HttpResponse
from django.template import loader

from .models import Question


def index(request):
    template = loader.get_template('Eventak/index.html')
    context = {
        
    }
    return HttpResponse(template.render(context, request))
