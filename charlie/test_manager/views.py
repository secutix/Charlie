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
    return HttpResponse("<!DOCTYPE html><html><head><title>Charlie Test Manager | Goodbye</title></head><body><p>Logged Out</p><p><a href='/login/'>Return to login page</a></p></body></html>")

@csrf_exempt
def home(request):
    """
        main administration custom page
    """
    return render_to_response('manage/home.html')

@csrf_exempt
def home_teams(request):
    """
        returns the tree with users and teams
    """
    json = []
    for t in list(Group.objects.all()):
        children = []
        for u in list(t.user_set.all()):
            children.append({'uid': u.id, 'text': u.username, 'leaf': True})
        json.append({'gid': t.id, 'text': t.name, 'draggable': False, 'children': children, 'expanded': True, 'iconCls': 'folder'})
    for u in list(User.objects.all()):
        if len(list(u.groups.all())) == 0:
            json.append({'uid': u.id, 'text': u.username, 'leaf': True})
    return HttpResponse(simplejson.dumps(json))

@csrf_exempt
def home_ts(request):
    """
        returns the tree of test sets
    """
    rts = list(TestSet.objects.filter(parent_test_set__id = 0))
    json = []
    for ts in rts:
        json.append(ts.build())
    ots = list(TestCase.objects.all())
    for t in ots:
        if len(t.test_sets.all()) == 0:
            json.append({'tsid': 0, 'text': t.title, 'value': t.id, 'leaf': True})
    return HttpResponse(simplejson.dumps(json))

@csrf_exempt
def manage_planning(request):
    if request.method == 'GET':
        return render_to_response('manage/planning.html')
    else:
        action = request.POST.get('action', '')
        json = []
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        if action == 'allSessionsData':
            user_set = []
            for t in list(TestSetRun.objects.filter(displayed = True)):
                for u in set(Group.objects.get(pk = t.group_id).user_set.all()):
                    user_set.append(u)
            user_set = list(set(user_set))
            for u in list(user_set):
                tcr = []
                for tr in (TestCaseRun.objects.filter(tester = u)):
                    tcr.append({'title': tr.title, 'execution_date': tr.execution_date, 'done': tr.done, 'id': tr.id})
                json.append({'user': u.username, 'uid': u.id, 'tcr': tcr})
        elif action == 'tcMove':
            #try:
            user = User.objects.get(username = request.POST.get('user', ''))
            tcr = TestCaseRun.objects.get(pk = int(request.POST.get('tcr', '')))
            y = int(request.POST.get('year', ''))
            m = int(request.POST.get('month', ''))
            d = int(request.POST.get('day', ''))
            date = datetime.date(y, m, d)
            tcr.tester = user
            tcr.execution_date = date
            tcr.save()
            json.append({'success': True})
            #except Exception:
                #json.append({'success': False, 'errorMessage': 'unable to move TC'})
        elif action == 'gettcr':
            user = User.objects.get(username = request.POST.get('user', ''))
            for tcr in list(TestCaseRun.objects.filter(tester = user)):
                json.append({
                    'title': tcr.title,
                    'execution_date': tcr.execution_date,
                    'id': tcr.id,
                })
        elif action == 'usersStore':
            for u in list(User.objects.all()):
                json.append({
                    'id': u.id,
                    'username': u.username,
                })
        else:
            pass
        return HttpResponse(simplejson.dumps(json, default = dthandler))

@csrf_exempt
def home_data(request):
    """
        test case set creation panel
    """
    json = []
    if request.method == 'GET':
        action = request.GET.get('action', '')
        if action == 'testSets':
            for tc in TestCase.objects.all():
                json.append({
                    'title': tc.title,
                    'id': tc.id,
                })
        elif action == 'deltc':
            TestCase.objects.get(pk = request.GET.get('tc', '')).delete()
            json = {'success': True}
        elif action == 'deluser':
            u = User.objects.get(pk = request.GET.get('u', ''))
            if u.id != request.session['uid']:
                u.delete()
                json = {'success': True}
            else:
                json = {'success': False, 'errorMessage': 'User is authenticated'}
        elif action == 'delteam':
            Group.objects.get(pk = request.GET.get('t', '')).delete()
            json = {'success': True}
        elif action == 'delts':
            TestSet.objects.get(pk=request.GET.get('ts', '')).delete()
            json = {'success': True}
        elif action == 'mvuser':
            u = User.objects.get(pk = request.GET.get('user', ''))
            for g in u.groups.all():
                u.groups.remove(g)
            u.save()
            gid = int(request.GET.get('team', ''))
            if gid != -1:
                g = Group.objects.get(pk = gid)
                u.groups.add(g)
                u.save()
            else:
                pass
            json = {'success': True}
        elif action == 'mvtc':
            tc = TestCase.objects.get(pk = request.GET.get('tc', ''))
            for cts in tc.get_sets():
                cts.test_cases.remove(tc)
            if request.GET.get('ts', '') != '-1':
                ts = TestSet.objects.get(pk = request.GET.get('ts', ''))
                ts.test_cases.add(tc)
            json = {'success': True}
        elif action == 'mvts':
            cts = TestSet.objects.get(pk = request.GET.get('cts', ''))
            if request.GET.get('pts', '') == '-1':
                cts.parent_test_set_id = 0
            else:
                cts.parent_test_set = TestSet.objects.get(pk = request.GET.get('pts', ''))
            cts.save()
            json = {'success': True}
        elif action == 'combodata':
            json = config.tc_data
        else:
            pass
    else:
        action = request.POST.get('action', '')
        if action == 'newtc':
            try:
                tsid = request.POST.get('tsid', '')
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
                if tsid != '-1':
                    ts = TestSet.objects.get(pk = tsid)
                    ts.test_cases.add(tc)
                    ts.save()
                else:
                    pass
                steps_remaining = True
                n = 1
                while steps_remaining:
                    try:
                        l1 = len(request.POST.get('action' + str(n), ''))
                        l2 = len(request.POST.get('expected' + str(n), ''))
                        if l1 == 0 or l2 == 0:
                            steps_remaining = False
                        else:
                            pass
                        n += 1
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
                json = {'success': True}
            except Exception as detail:
                json = {'success': False, 'errorMessage': detail.message}
        elif action == 'newUser':
            u = User(username = request.POST.get('username', ''))

            # TODO : set user permissions

            u.save()
            if request.POST.get('team', '') != '-1':
                u.groups.add(Group.objects.get(pk = request.POST.get('team', '')))
                privileged = request.POST.get('privileged', '')
                user.user_permissions = [
                    'test_manager.change_availability',
                    'test_manager.add_jira',
                    'test_manager.change_jira',
                    'test_manager.change_testcaserun',
                    'test_manager.change_testcasesteprun',
                ]
                if privileged == 'on':
                    user.user_permissions.add('test_manager.add_tag')
                    user.user_permissions.add('test_manager.change_tag')
                    user.user_permissions.add('test_manager.delete_tag')
                    user.user_permissions.add('test_manager.add_testcase')
                    user.user_permissions.add('test_manager.change_testcase')
                    user.user_permissions.add('test_manager.add_testcasestep')
                    user.user_permissions.add('test_manager.change_testcasestep')
                    user.user_permissions.add('test_manager.delete_testcasestep')
                    user.user_permissions.add('test_manager.add_testcaserun')
                    user.user_permissions.add('test_manager.add_testcasesteprun')
                    user.user_permissions.add('test_manager.delete_testcasesteprun')
                u.save()
            else:
                pass
            json = {'success': True}
        elif action == 'newTeam':
            g = Group(name = request.POST.get('name', ''))
            g.save()
            json = {'success': True}
        elif action == 'testSets':
            test_set_name = request.POST.get('testSetName', '')
            ptsi = int(request.POST.get('parentTestSetId', ''))
            n = 0
            while True:
                try:
                    current_tc = request.POST.get('tc' + str(n), '')
                    l = len(current_tc)
                    if l == 0:
                        break
                    else:
                        pass
                    n += 1
                except (TypeError, KeyError):
                    break
            ts = TestSet(
                name = test_set_name,
                parent_test_set_id = ptsi,
            )
            ts.save()
            for i in range(n):
                ts.test_cases.add(TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))))
            ts.save()
            json = {'success': True}
        else:
            pass
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
        return render_to_response('test_manager/create_tc.html', c)

@csrf_exempt
def create_tc_data(request):
    """
        returns the content of the dropdown fields of the form
    """
    return HttpResponse(simplejson.dumps(config.tc_data))

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
                l1 = len(request.POST.get('action' + str(n), ''))
                l2 = len(request.POST.get('expected' + str(n), ''))
                if l1 == 0 or l2 == 0:
                    steps_remaining = False
                else:
                    pass
                n += 1
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
