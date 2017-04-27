import json
import datetime
from urllib.parse import urlencode, unquote
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Classifier, Classes, Classification
from classifier.apps import ClassifierConfig
from .forms import NameForm, MessageForm
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from classifier.serializers import ClassificationSerializer

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


@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def classifications_collection(request):
    if request.method == 'GET':
        posts = Classification.objects.all()
        serializer = ClassificationSerializer(posts, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
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
        data = {'data': request.data.get('message'),
                'user': user,
                'result': short_result,
                'ip_address': ip_address,
                'date': now}
        serializer = ClassificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def classifications_element(request, pk):
    try:
        post = Classification.objects.get(pk=pk)
    except Classification.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ClassificationSerializer(post)
        return Response(serializer.data)