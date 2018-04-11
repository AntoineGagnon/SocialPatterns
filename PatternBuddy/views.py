import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
# Create your views here.
from django.urls import reverse
from django.views import generic
from excel_response import ExcelResponse

from PatternBuddy.models import Repository
from PatternBuddy.repository_loader import load_from_github, analyze_repo, get_repo_api

logger = logging.getLogger(__name__)


class IndexListView(generic.ListView):
    model = Repository
    context_object_name = 'recent_repo_list'
    queryset = Repository.objects.all()
    template_name = "PatternBuddy/index.html"


class DetailView(generic.DetailView):
    model = Repository
    template_name = 'PatternBuddy/repository.html'


def submit(request):
    repository_name = request.POST['repo_textfield']
    logger.warning("repo_name = " + repository_name)
    try:
        repository = Repository.objects.get(full_name__icontains=repository_name)
        logger.debug("Repo found")
    except ObjectDoesNotExist:
        repository = load_from_github(repository_name=repository_name)
        if repository is None:
            return HttpResponse("The repository you entered does not exist")
    if not repository.dp_analyzed:
        analyze_repo(get_repo_api(repository_name), repository)
    return HttpResponseRedirect(reverse('repository:detail', args=(repository.id,)))


def save_to_xlsx(request):
    data = Repository.objects.all()
    return ExcelResponse(data, "data_socialpatterns")
