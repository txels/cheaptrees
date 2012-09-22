from django.views.generic import DetailView
from cheaptrees.models import Thread


class ThreadDetail(DetailView):
    context_object_name = 'thread'
    queryset = Thread.objects.all()
