import re
from django.apps import AppConfig
from opentc.client import Client


class ClassifierConfig(AppConfig):
    name = 'classifier'
    verbose_name = "Open Text Classification - Web"
    opentc = Client()
    remove_newline = re.compile('\r?\n')

    def ready(self):
        print("OpenTC Initialization")
        pass # startup code here
