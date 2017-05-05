from django.contrib import admin

from .models import Classifier, Classes, Classification, Wikipedia

admin.site.register(Classifier)
admin.site.register(Classes)
admin.site.register(Classification)
admin.site.register(Wikipedia)
