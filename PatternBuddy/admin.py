from django.contrib import admin

from .models import Repository, DesignPattern, Language, PatternInRepo

# Register your models here.
admin.site.register(Repository)
admin.site.register(DesignPattern)
admin.site.register(PatternInRepo)
admin.site.register(Language)