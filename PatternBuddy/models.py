import re

from django.core.exceptions import ObjectDoesNotExist
from github import Github
from django.db import models


# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Repository(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    repo_name = models.CharField(max_length=200)
    last_checked = models.DateField(auto_now=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "repositories"

    def __str__(self):
        return self.repo_name

    @classmethod
    def load_from_github(cls, repository_name):
        repository_name = re.sub(r'^(http(s)*://)*github.com/', '', repository_name)
        g = Github("***REMOVED***")
        repo_api = g.get_repo(repository_name)
        try:
            repo_api.name
        except Exception:
            return None
        repo = Repository(id=repo_api.id,repo_name=repo_api.name)
        try:
            repo.language = Language.objects.get(name=repo_api.language)
        except ObjectDoesNotExist:
            new_language = Language(name=repo_api.language)
            new_language.save()
            repo.language = new_language
        repo.save()
        return repo


class DesignPattern(models.Model):
    design_name = models.CharField(max_length=50)

    def __str__(self):
        return self.design_name


class PatternInRepo(models.Model):
    file_name = models.CharField(max_length=200)
    design_pattern = models.ForeignKey(DesignPattern, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "patterns in repos"

    def __str__(self):
        return "Pattern: " + str(self.design_pattern) + " in Repository: " + \
               str(self.repository) + " at file: " + self.file_name
