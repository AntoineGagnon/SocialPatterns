import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.views import generic

from PatternBuddy.models import Repository

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "PatternBuddy/index.html")


class DetailView(generic.DetailView):
    model = Repository
    template_name = 'PatternBuddy/repository.html'


def submit(request):
    repository_name = request.POST['repo_textfield']
    try:
        repository = Repository.objects.get(repo_name__icontains=repository_name)
    except ObjectDoesNotExist:
        repository = Repository.load_from_github(repository_name)
    return HttpResponseRedirect(reverse('repository:detail', args=(repository.id,)))
