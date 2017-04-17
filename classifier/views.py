from urllib.parse import urlencode, unquote
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
import re
from .models import Classifier, Classes
from classifier.apps import ClassifierConfig
from .forms import NameForm, MessageForm

def index(request):
    classifier_list = Classifier.objects.order_by('name')[:5]
    context = {'classifier_list': classifier_list}
    return render(request, 'classifier/index.html', context)


def detail(request, classifier_id):
    classifier = get_object_or_404(Classifier, pk=classifier_id)
    return render(request, 'classifier/detail.html', {'classifier': classifier})


def predict(request):
    response = ClassifierConfig.opentc.command("PING\n")
    response = json.loads(response.decode('utf-8'))
    print("response: {}".format(response))
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            message = ClassifierConfig.remove_newline.sub(' ', message)
            response = ClassifierConfig.opentc.predict_stream(message.encode("utf-8"))
            result = json.loads(response.decode('utf-8'))["result"]
            request.session['data'] = result
            # return render(request, 'classifier/predict.html', {'form': form})
            return HttpResponseRedirect(reverse('classifier:predict_result'))
    else:
        form = MessageForm()
    return render(request, 'classifier/predict.html', {'form': form})


def predict_result(request):
    data = request.session.get("data")
    return render(request, 'classifier/predict_result.html', {'data': data})


@csrf_exempt
def request_submit(request):
    data = {"result": ""}
    if request.method == "POST":
        if "result" in request.POST:
            result = request.POST["result"]
            # if re.match("^[A-Za-z0-9\.\[\]\{\}\'\",: ]*$", result):
            if ClassifierConfig.input_data_validity.search(result):
                data = {"result": request.POST["result"]}
    encoded = urlencode(data)
    redirect_url = "http://{}{}?{}".format(request.META['HTTP_HOST'],
                                           reverse('classifier:request_info'),
                                           encoded)
    return HttpResponseRedirect(redirect_url)


def request_info(request):
    data = request.GET.get("result", "{}")
    # if re.match("^[A-Za-z0-9\.\[\]\{\}\'\",: ]*$", data):
    if ClassifierConfig.input_data_validity.search(data):
        try:
            result = json.loads(data)
            return render(request, 'classifier/request_info.html', {'result': result})
        except ValueError:
            return render(request, 'classifier/request_info.html', {'error_message': "The input data is not valid"})
    else:
        return render(request, 'classifier/request_info.html', {'error_message': "The input data is not valid"})