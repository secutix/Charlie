from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from test_manager.models import *
from test_manager.classes import Jiraconnection
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from test_manager.config import *
import simplejson

def login_view(request):
    redirect = 'login'
    if request.method == "GET":
        try:
            logout(request)
        except Exception:
            pass
        c = {}
        c.update(csrf(request))
        return render_to_response('test_manager/login.html', c)
    elif request.method == "POST":
        user = authenticate(user_name=request.POST['login'], password=request.POST['password'])
        if user is not None:
            request.session['uid'] = user.id
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
def planning_data(request):
    if request.user.is_authenticated():
        tcr = TestCaseRun.objects.filter(tester = request.session['uid'])
        json = []
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        for t in tcr:
            json.append({
                'title': t.title,
                'execution_date': t.execution_date,
                'id': t.id,
                })
            return HttpResponse(simplejson.dumps(json, default=dthandler))
    else:
        return HttpResponse(simplejson.dumps({'success': 'false', 'error': 'user is not authenticated'}))

@csrf_exempt
def planning(request):
    if request.method == 'GET':
        try:
            c = Context({'tester_visa': User.objects.get(pk = request.session['uid']).username.upper()})
            return render_to_response('test_manager/planning.html', c)
        except KeyError:
            return HttpResponseRedirect('/test_manager/login/')
    else:
        try:
            tcr = TestCaseRun.objects.get(pk = request.POST['tcr'])
            tcr.execution_date = datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
            tcr.save()
            json = simplejson.dumps({'success': 'true'})
        except Exception:
            json = simplejson.dumps({'success': 'false'})
        return HttpResponse(json)

@csrf_exempt
def availabilities(request):
    return HttpResponse('Availabilities')

@csrf_exempt
def create_tc(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/test_manager/login/')
    else:
        c = Context({'tester_visa': User.objects.get(pk = request.session['uid']).username.upper()})
        return render_to_response('test_manager/create_tc_ext.html', c)

@csrf_exempt
def create_tc_data(request):
    json = simplejson.dumps(tc_data)
    return HttpResponse(simplejson.dumps(tc_data))

@csrf_exempt
def create_tc_updt(request):
    try:
        title = request.POST['title']
        description = request.POST['description']
        precondition = request.POST['precondition']
        envir = request.POST['envir']
        os = request.POST['os']
        browser = request.POST['browser']
        release = request.POST['release']
        version = request.POST['version']
        module = request.POST['module']
        smodule = request.POST['smodule']
        criticity = request.POST['criticity']
        tc = TestCase(title = title,
            description = description,
            author = User.objects.get(pk = request.session['uid']),
            environment = envir,
            os = os,
            browser = browser,
            release = release,
            version = version,
            module = module,
            sub_module = smodule,
            criticity = int(criticity),
            precondition = precondition
        )
        tc.save()
        steps_remaining = True
        n = 1
        while steps_remaining:
            try:
                request.POST['action' + str(n)]
                request.POST['expected' + str(n)]
                n = n + 1
            except (KeyError, TypeError):
                steps_remaining = False
        for i in range(n - 1):
            st = TestCaseStep(
                num = i + 1,
                action = request.POST['action' + str(i + 1)],
                expected = request.POST['expected' + str(i + 1)],
                test_case = tc
            )
            st.save()
        return HttpResponse(simplejson.dumps({'success': True}))
    except Exception as detail:
        return HttpResponse(simplejson.dumps({'success': False, 'errorMessage': detail}))
