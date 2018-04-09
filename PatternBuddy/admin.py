from django.contrib import admin

from .models import Repository, DesignPattern, Language, PatternInRepo, Contributor, Contribution, ClassFileWithPattern

# Register your models here.
admin.site.register(Repository)
admin.site.register(DesignPattern)
admin.site.register(PatternInRepo)
admin.site.register(Language)
admin.site.register(Contributor)
admin.site.register(Contribution)
admin.site.register(ClassFileWithPattern)
