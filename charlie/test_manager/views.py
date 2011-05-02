from django.shortcuts import render_to_response
from django.http import HttpResponse
from test_manager.models import *
from test_manager.classes import *
from django.core.context_processors import csrf
import pickle

def login(request):
    if request.method == "GET":
        c = {}
        c.update(csrf(request))
        return render_to_response('tests/login.html', c)
    elif request.method == "POST":
        jc = Jiraconnection(request.POST['visa'], request.POST['passwd'])
        if jc.success:
            return HttpResponse("connected")
        else:
            return HttpResponse("failed to connect")
    else:
        return HttpResponse("bad http request")

def create_tc(request):
    return render_to_response('tests/create_tc.html')

def make_update(request, postdata):
    if request.method == 'GET':
        return render_to_response('tests/create_tc.html')
    elif request.method == 'POST':
        return render_to_response('tests/make_update.html')
