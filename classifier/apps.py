import re
from django.apps import AppConfig
from opentc.client import Client


class ClassifierConfig(AppConfig):
    name = 'classifier'
    verbose_name = "Open Text Classification - Web"
    opentc = Client()
    remove_newline = re.compile('\r?\n')
    input_data_validity = re.compile("^[A-Za-z0-9\.\[\]\{\}\'\",: ]*$")

    def ready(self):
        print("OpenTC Initialization")
        pass # startup code here
