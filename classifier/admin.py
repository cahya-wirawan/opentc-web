from django.contrib import admin

from .models import Classifier, Classes, Classification

admin.site.register(Classifier)
admin.site.register(Classes)
admin.site.register(Classification)
