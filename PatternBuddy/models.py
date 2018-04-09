from django.db import models


# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Repository(models.Model):


    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    last_checked = models.DateField(auto_now=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    pull_request_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    contributors_count = models.PositiveIntegerField(default=0)
    size = models.PositiveIntegerField(default=0)
    dp_count = models.PositiveIntegerField(default=0)

    def get_contributions(self):
        return Contribution.objects.filter(repository=self)

    def get_comment_pr_ratio(self):
        return self.comments_count/self.pull_request_count

    def get_dp_count(self):
        return self.patterninrepo_set.count()

    class Meta:
        verbose_name_plural = "repositories"

    def __str__(self):
        return self.full_name


class DesignPattern(models.Model):
    design_name = models.CharField(max_length=50)

    def __str__(self):
        return self.design_name


class Contributor(models.Model):
    login = models.CharField(max_length=200)
    followers_count = models.PositiveIntegerField(default=0)
    commits_count = models.PositiveIntegerField(default=0)
    url = models.URLField()

    def __str__(self):
        return self.login


class Contribution(models.Model):
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Contribution of " + str(self.contributor) + " on " + str(self.repository)


class PatternInRepo(models.Model):
    modifications_count = models.PositiveIntegerField(default=1)
    design_pattern = models.ForeignKey(DesignPattern, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "patterns in repos"

    def __str__(self):
        return "Pattern: " + str(self.design_pattern) + " in Repository: " + \
               str(self.repository)


class ClassFileWithPattern(models.Model):
    modifications_count = models.PositiveIntegerField(default=1)
    pattern_in_repo = models.ForeignKey(PatternInRepo, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=200,default="ClassName")
    url = models.URLField(default="https://github.com")
    role = models.CharField(max_length=200,default="role")

    def __str__(self):
        return "File " + self.class_name + " has pattern " + self.pattern_in_repo.design_pattern.design_name
