from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from test_manager.models import *
from test_manager.classes import Jiraconnection
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
import simplejson

def login_view(request):
    redirect = 'login'
    if request.method == "GET":
        c = {}
        c.update(csrf(request))
        return render_to_response('test_manager/login.html', c)
    elif request.method == "POST":
        user = authenticate(user_name=request.POST['login'], password=request.POST['password'])
        request.session['login'] = user.id
        request.session.set_test_cookie()
        if user is not None:
            login(request, user)
            redirect = 'planning'
        else:
            pass
    else:
        pass
    return HttpResponseRedirect('/test_manager/' + redirect)

def logout_view(request):
    logout(request)
    return HttpResponse("<p>Logged Out</p><p><a href='/test_manager/login/'>Return to login page</a></p>")

@csrf_exempt
def planning_ctl(request):
    tcr = TestCaseRun.objects.filter(tester = request.session['login'])
    json = []
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    for t in tcr:
        json.append({
            'title': t.title,
            'execution_date': t.execution_date,
        })
    return HttpResponse(simplejson.dumps(json, default=dthandler))


@csrf_exempt
def planning(request):
    if request.session.get('login') == None:
        return HttpResponseRedirect('/test_manager/login/')
    else:
        return render_to_response('test_manager/planning.html')

def create_tc(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/test_manager/login/?next=%s' % request.path)
    return render_to_response('test_manager/create_tc.html')

def make_update(request, postdata):
    if request.method == 'GET':
        return render_to_response('test_manager/create_tc.html')
    elif request.method == 'POST':
        return render_to_response('test_manager/make_update.html')
