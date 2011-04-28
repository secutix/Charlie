from django.core import serializers
from django.shortcuts import render_to_response
from django.http import HttpResponse
from test_manager.models import *
from django.core.context_processors import csrf
from test_manager.classes import *

def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('tests/login.html', c)

def login_attempt(request):
    c = {}
    c.update(csrf(request))
    visa = request.POST['visa']
    password = request.POST['pass']
    connection = JiraConnection(visa, password)
    return serializers.serialize('json', connection)

def create_tc(request):
    return render_to_response('tests/create_tc.html')

def make_update(request, postdata):
    if request.method == 'GET':
        return render_to_response('tests/create_tc.html')
    elif request.method == 'POST':
        return render_to_response('tests/make_update.html')
