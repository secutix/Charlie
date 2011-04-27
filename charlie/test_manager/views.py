from django.shortcuts import render_to_response
from test_manager.models import *

def create_tc(request):
    return render_to_response('test_manager/create_tc.html')

def make_update(request, postdata):
    if request.method == 'GET':
        return render_to_response('test_manager/create_tc.html')
    elif request.method == 'POST':
        return render_to_response('test_manager_make_update.html')
