from django.views import generic
from django.views.generic import TemplateView
from django.db.models import Min
from sportsrec.models import *
import datetime
from django.http import HttpResponse


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

class Index(generic.TemplateView):
    template_name='sportsrec/index.html'
    context_object_name='index'
