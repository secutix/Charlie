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
    """
        login page
    """
    redirect = '/login/'
    if request.method == "GET":
        try:
            logout(request)
        except Exception:
            pass
        c = {}
        c.update(csrf(request))
        return render_to_response('test_manager/login.html', c)
    elif request.method == "POST":
        user = authenticate(user_name=request.POST.get('login', ''), password=request.POST.get('password', ''))
        if user is not None:
            request.session['uid'] = user.id
            login(request, user)
            if user.is_staff:
                redirect = '/manage/home'
            else:
                redirect = '/test_manager/planning/'
        else:
            pass
    else:
        pass
    return HttpResponseRedirect(redirect)

def logout_view(request):
    """
        logout page
    """
    logout(request)
    return HttpResponse("<!DOCTYPE html><html><head><title></title></head><body><p>Logged Out</p><p><a href='/login/'>Return to login page</a></p></body></html>")

@csrf_exempt
def home(request):
    """
        main administration custom page
    """
    return render_to_response('manage/home.html')

@csrf_exempt
def home_data(request):
    """
        test case set creation panel
    """
    if request.method == 'GET':
        json = []
        action = request.GET.get('action', '')
        if action == 'testSets':
            for tc in TestCase.objects.all():
                json.append({
                    'title': tc.title,
                    'id': tc.id,
                })
        else:
            pass
    else:
        try:
            action = request.POST.get('action', '')
            print action
            test_set_name = request.POST.get('testSetName', '')
            print test_set_name
            tcs_remaining = True
            n = 0
            while tcs_remaining:
                try:
                    l = len(request.POST.get('tc' + str(n), ''))
                    if l == 0:
                        tcs_remaining = False
                    else:
                        pass
                    n += 1
                except (TypeError, KeyError):
                    tcs_remaining = False
            ts = TestSet(
                name = test_set_name,
                parent_test_set_id = 0,
            )
            ts.save()
            for i in range(n - 1):
                ts.test_cases.add(TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))))
            ts.save()
            json = {'success': True}
        except Exception as detail:
            json = {'success': False, 'errorMessage': detail}
    return HttpResponse(simplejson.dumps(json))

@csrf_exempt
def home_menu(request):
    """
        returns the list of admin pages
    """
    return HttpResponse(simplejson.dumps(config.main_menu))

@csrf_exempt
def planning_data(request):
    """
        returns the list of test case runs the logged in user has to perform
    """
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
        return HttpResponse(simplejson.dumps({'success': False, 'errorMessage': 'user is not authenticated'}))

@csrf_exempt
def planning(request):
    """
        planning page (main page for testers)
    """
    if request.method == 'GET':
        try:
            user = User.objects.get(pk = request.session['uid'])
            if user.is_staff:
                return HttpResponseRedirect('/manage/home/')
            else:
                pass
        except Exception:
            pass
        try:
            c = Context({'tester_visa': User.objects.get(pk = request.session['uid']).username.upper()})
            return render_to_response('test_manager/planning.html', c)
        except KeyError:
            return HttpResponseRedirect('/login/')
    else:
        try:
            tcr = TestCaseRun.objects.get(pk = request.POST.get('tcr', ''))
            tcr.execution_date = datetime.date(int(request.POST.get('year', '')), int(request.POST.get('month', '')), int(request.POST.get('day', '')))
            tcr.save()
            json = simplejson.dumps({'success': True})
        except Exception as detail:
            json = simplejson.dumps({'success': False, 'errorMessage': detail})
        return HttpResponse(json)

@csrf_exempt
def availabilities(request):
    """
        a page to save one's own availabilities
    """
    return HttpResponse('Availabilities')

@csrf_exempt
def create_tc(request):
    """
        test case creation page
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    else:
        c = Context({'tester_visa': User.objects.get(pk = request.session['uid']).username.upper()})
        return render_to_response('test_manager/create_tc_ext.html', c)

@csrf_exempt
def create_tc_data(request):
    """
        returns the content of the dropdown fields of the form
    """
    return HttpResponse(simplejson.dumps(tc_data))

@csrf_exempt
def create_tc_updt(request):
    """
        save the new test case and redirect to the planning
    """
    try:
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        precondition = request.POST.get('precondition', '')
        envir = request.POST.get('envir', '')
        os = request.POST.get('os', '')
        browser = request.POST.get('browser', '')
        release = request.POST.get('release', '')
        version = request.POST.get('version', '')
        module = request.POST.get('module', '')
        smodule = request.POST.get('smodule', '')
        criticity = request.POST.get('criticity', '')
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
                request.POST.get('action' + str(n), '')
                request.POST.get('expected' + str(n), '')
                n = n + 1
            except (KeyError, TypeError):
                steps_remaining = False
        for i in range(n - 1):
            st = TestCaseStep(
                num = i + 1,
                action = request.POST.get('action' + str(i + 1), ''),
                expected = request.POST.get('expected' + str(i + 1), ''),
                test_case = tc
            )
            st.save()
        return HttpResponse(simplejson.dumps({'success': True}))
    except Exception as detail:
        return HttpResponse(simplejson.dumps({'success': False, 'errorMessage': detail}))
