from django.contrib import admin

from .models import Classifier, Classes

admin.site.register(Classifier)
admin.site.register(Classes)
