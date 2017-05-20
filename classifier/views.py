import json
import datetime
from urllib.parse import urlencode, unquote
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from bs4 import BeautifulSoup
import urllib.request
from random import choice
from .forms import NameForm, MessageForm
from classifier.serializers import ClassificationSerializer
from .models import Classifier, Classes, Classification, Wikipedia
from classifier.apps import ClassifierConfig


def index(request):
    classifier_list = Classifier.objects.order_by('name')[:5]
    context = {'classifier_list': classifier_list}
    return render(request, 'classifier/index.html', context)


def detail(request, classifier_id):
    classifier = get_object_or_404(Classifier, pk=classifier_id)
    return render(request, 'classifier/detail.html', {'classifier': classifier})


def predict(request):
    form = MessageForm()
    ga_id = None
    if hasattr(settings, "GOOGLE_ANALYTICS_PROPERTY_ID"):
        ga_id = settings.GOOGLE_ANALYTICS_PROPERTY_ID
    return render(request, 'classifier/predict.html', {'form': form, 'ga_id': ga_id})


def predict_result(request):
    data = request.session.get("data")
    return render(request, 'classifier/predict_result.html', {'data': data})


@api_view(['GET'])
def get_random_article(request):
    base_url = "https://en.wikipedia.org/wiki/Special:RandomInCategory/"
    categories = Wikipedia.objects.all()
    if len(categories) == 0:
        category = "Medicine"
    else:
        category = str(choice(categories))
    url = base_url + category
    content_text = ""
    while True:
        with urllib.request.urlopen(url) as response:
            html_doc = response.read()
            soup = BeautifulSoup(html_doc, 'html.parser')
            content_html = soup.find(id="mw-content-text")
            content_text = " ".join(content_html.get_text().replace("\n", " ").split(" ")[:256]).strip()
            if content_text.startswith("Subcategories") or content_text.startswith("This") \
                    or content_text.startswith("Wikimedia") or content_text.startswith("The main article"):
                continue
            break
    response = {"article": content_text}
    return Response(JSONRenderer().render(response))

@csrf_exempt
def request_submit(request):
    data = {"result": ""}
    if request.method == "POST":
        if "type" in request.POST and "result" in request.POST:
            type = request.POST["type"]
            result = request.POST["result"]
            # if re.match("^[A-Za-z0-9\.\[\]\{\}\'\",: -]*$", result):
            if ClassifierConfig.input_data_validity.search(type) and \
                    ClassifierConfig.input_data_validity.search(result):
                data = {"type": request.POST["type"], "result": request.POST["result"]}
    encoded = urlencode(data)
    redirect_url = "http://{}{}?{}".format(request.META['HTTP_HOST'],
                                           reverse('classifier:request_info'),
                                           encoded)
    return HttpResponseRedirect(redirect_url)


def request_info(request):
    type = request.GET.get("type", "ml")
    data = request.GET.get("result", "{}")
    # if re.match("^[A-Za-z0-9\.\[\]\{\}\'\",: -]*$", data):
    if ClassifierConfig.input_data_validity.search(data):
        try:
            result = json.loads(data)
            return render(request, 'classifier/request_info.html', {'type': type, 'result': result})
        except ValueError:
            return render(request, 'classifier/request_info.html', {'error_message': "The input data is not valid"})
    else:
        return render(request, 'classifier/request_info.html', {'error_message': "The input data is not valid"})


@api_view(['GET'])
@login_required
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def classifications_collection(request):
    posts = Classification.objects.order_by('-date')[:5]
    serializer = ClassificationSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@login_required
def classifications_element(request, pk):
    try:
        post = Classification.objects.get(pk=pk)
    except Classification.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ClassificationSerializer(post)
        return Response(serializer.data)


@api_view(['POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def prediction(request):
    message = request.data.get('message')
    message = ClassifierConfig.remove_newline.sub(' ', message)
    response = ClassifierConfig.opentc.predict_stream(message.encode("utf-8"))
    result = json.loads(response.decode('utf-8'))["result"]
    short_result = json.dumps(result)
    classifiers = []
    for key in result:
        classifiers.append(key)
    for key in classifiers:
        result[settings.CLASSIFIERS[key]] = result.pop(key)
    result = json.dumps(result)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    if request.user.username == "":
        user = "anonymous"
    else:
        user = request.user.username
    now = datetime.datetime.now()
    data = {'data': request.data.get('message')[:1024],
            'user': user,
            'result': short_result,
            'ip_address': ip_address,
            'date': now}
    serializer = ClassificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
