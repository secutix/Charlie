from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from test_manager.models import *
from django.core.context_processors import csrf
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import logout, login, authenticate
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from suds.client import Client
from test_manager.config import *
import simplejson
import logging
import unicodedata

def main_page(request):
    """
        handles requests to the root of the website
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        return HttpResponseRedirect('/manage/home/')
    else:
        return HttpResponseRedirect('/test_manager/planning/')

def login_view(request):
    """
        login page
    """
    redirect = '/login/'
    if request.method == "GET":
        c = {}
        try:
            if len(request.session['login']) > 0:
                c = {'username': request.session['login'], 'error': True}
                request.session['login'] = ''
            else:
                pass
        except Exception:
            pass
        c.update(csrf(request))
        return render_to_response('test_manager/login.html', c)
    elif request.method == "POST":
        user = authenticate(user_name=request.POST.get('login', ''), password=request.POST.get('password', ''))
        if user is not None:
            request.session['uid'] = user.id
            try:
                login(request, user)
                try:
                    request.session['auth'] = user.cust_auth
                except Exception:
                    logging.warning('Could not store the authentication for Jira in the session')
                if user.is_staff:
                    logging.info("Admin %s logged in" % user.username)
                    json = {'success': True, 'next': '/manage/home/'}
                else:
                    logging.info("User %s logged in" % user.username)
                    json = {'success': True, 'next': '/test_manager/planning/'}
            except Exception as detail:
                logging.error('Error during loging : %s' % detail)
        else:
            logging.error('User %s could not log in' % request.POST.get('login', ''))
            request.session['login'] = request.POST.get('login', '')
            json = {'success': False, 'next': '/login/'}
        return HttpResponse(simplejson.dumps(json))
    else:
        logging.error('bad request')
        return HttpResponseRedirect(redirect)

def logout_view(request):
    """
        logout page
    """
    logging.info("User %s logged out" % User.objects.get(pk = request.session['uid']).username)
    logout(request)
    return HttpResponseRedirect("/login/")

def manage_avails(request):
    """
        Controller for the "Availabilities" admin view
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        if request.method == 'GET':
            action = request.GET.get('action', '')
            if len(action) == 0:
                tsrid = int(request.GET.get('tsrid', ''))
                f_date = TestSetRun.objects.get(pk = tsrid).from_date
                y = f_date.year
                m = f_date.month
                d = f_date.day
                c = {'tsrid': tsrid, 'd': d, 'm': m, 'y': y}
                c.update(csrf(request))
                return render_to_response('manage/avails.html', c)
            else:
                json = []
                if action == 'allAvails':
                    try:
                        tsr = TestSetRun.objects.get(pk = int(request.GET.get('tsrid', '')))
                        usrs = list(tsr.group.user_set.all())
                        for u in usrs:
                            avs = []
                            for a in Availability.objects.filter(user = u, day__gte = tsr.from_date, day__lte = tsr.to_date):
                                avs.append({
                                    'pct': a.avail,
                                    'title': str(a.avail) + '%',
                                    'execution_date': a.day,
                                    'tcrid': a.id,
                                    'uid': u.id,
                                    'user': u.username,
                                })
                            json.append({'user': u.username, 'avails': avs})
                    except Exception as detail:
                        logging.error('Couldn\'t load the data : %s' % detail)
                        json = {'success': False, 'errorMessage': 'Couldn\'t load the data'}
                else:
                    pass
            return HttpResponse(simplejson.dumps(json, default = dthandler))
        else:
            json = []
            action = request.POST.get('action', '')
            if action == 'chgavail':
                try:
                    y = int(request.POST.get('y', ''))
                    m = int(request.POST.get('m', ''))
                    d = int(request.POST.get('d', ''))
                    c_day = datetime.date(y, m, d)
                    pct = int(request.POST.get('pct', ''))
                    c_user = User.objects.get(pk = int(request.POST.get('uid', '')))
                    a = Availability.objects.get(user = c_user, day = c_day)
                    a.avail = pct
                    a.save()
                    logging.info('changed %s\'s availability to %d on %r' % (c_user.username, pct, c_day))
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Unable to change availability : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Unable to change this user\'s availability'}
            else:
                pass
            return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseRedirect('/')


def manage_planning(request):
    """
        Controller for the "Current sessions" view
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        json = []
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        if request.method == 'GET':
            action = request.GET.get('action', '')
            if len(action) > 0:
                if action == 'allSessionsData':
                    try:
                        tsrid = int(request.GET.get('tsr_filter', ''))
                        t = TestSetRun.objects.get(pk = tsrid)
                        f_d = t.from_date
                        t_d = t.to_date
                        user_set = []
                        for u in set(Group.objects.get(pk = t.group_id).user_set.all().order_by('username')):
                            user_set.append(u)
                        user_set = list(set(user_set))
                        for u in list(user_set):
                            avails = Availability.objects.filter(day__gte = f_d, day__lte = t_d, user = u)
                            avs = []
                            for a in avails:
                                avs.append({
                                    'day': a.day,
                                    'time': a.remaining_time(),
                                })
                            tcr = []
                            for tr in list(TestCaseRun.objects.filter(tester = u, test_set_run = t).order_by('id')):
                                tcr.append({
                                    'title': tr.title,
                                    'execution_date': tr.execution_date,
                                    'length': tr.length,
                                    'qtip': str(tr.length) + ' min : ' + tr.description,
                                    'status': tr.status,
                                    'tcrid': tr.id,
                                })
                            json.append({'user': u.username.upper(), 'uid': u.id, 'tcr': tcr, 'avails': avs})
                    except ValueError:
                        user_set = []
                        f_d = datetime.date.today()
                        t_d = datetime.date.today()
                        for t in list(TestSetRun.objects.filter(displayed = True).order_by('name')):
                            if f_d > t.from_date:
                                f_d = t.from_date
                            else:
                                pass
                            if t_d < t.to_date:
                                t_d = t.to_date
                            else:
                                pass
                            for u in set(Group.objects.get(pk = t.group_id).user_set.all().order_by('username')):
                                user_set.append(u)
                        user_set = list(set(user_set))
                        for u in list(user_set):
                            avails = Availability.objects.filter(day__gte = f_d, day__lte = t_d, user = u)
                            avs = []
                            for a in avails:
                                avs.append({
                                    'day': a.day,
                                    'time': a.remaining_time(),
                                })
                            tcr = []
                            for tr in list(TestCaseRun.objects.filter(tester = u).order_by('title')):
                                if tr.test_set_run.displayed:
                                    tcr.append({
                                        'title': tr.title,
                                        'execution_date': tr.execution_date,
                                        'length': tr.length,
                                        'qtip': str(tr.length) + ' min : ' + tr.description,
                                        'status': tr.status,
                                        'tcrid': tr.id
                                    })
                            json.append({'user': u.username.upper(), 'uid': u.id, 'tcr': tcr, 'avails': avs})
                else:
                    pass
                return HttpResponse(simplejson.dumps(json, default = dthandler))
            else:
                try:
                    tsr = TestSetRun.objects.get(pk = int(request.GET.get('tsr', '')))
                    f_date = tsr.from_date
                    tsr_filter = request.GET.get('tsr', '')
                except Exception:
                    tcrid = request.GET.get('tcrid', '')
                    if len(tcrid) > 0:
                        tsr = TestCaseRun.objects.get(pk = int(tcrid)).test_set_run
                        f_date = tsr.from_date
                        tsr_filter = tsr.id
                    else:
                        tsr_filter = 'all'
                        f_date = datetime.date.today()
                y = f_date.year
                m = f_date.month
                d = f_date.day
                c = {'d': d, 'm': m, 'y': y, 'tsr_filter': tsr_filter}
                c.update(csrf(request))
                return render_to_response('manage/planning.html', c)
        else:
            action = request.POST.get('action', '')
            if action == 'tcMove':
                try:
                    try:
                        user = User.objects.get(username = request.POST.get('user', ''))
                    except User.DoesNotExist:
                        user = User.objects.get(pk = int(request.POST.get('user', '')))
                    tcr = TestCaseRun.objects.get(pk = int(request.POST.get('tcr', '')))
                    y = int(request.POST.get('year', ''))
                    m = int(request.POST.get('month', ''))
                    d = int(request.POST.get('day', ''))
                    date = datetime.date(y, m, d)
                    try:
                        Availability.objects.get(day = date, user = user)
                    except Availability.DoesNotExist:
                        Availability(
                            day = date,
                            user = user,
                            group = user.groups.all()[0],
                        ).save()
                    tcr.tester = user
                    tcr.execution_date = date
                    tcr.save()
                    logging.info("Test Case Run %s moved to %s on %s's calendar" % (tcr.title, date.isoformat(), user.username))
                    json.append({'success': True})
                except Exception as detail:
                    logging.error("unable to move test case. %s" % detail)
                    json.append({'success': False, 'errorMessage': 'unable to move TC'})
            elif action == 'newTcr':
                try:
                    tc = TestCase.objects.get(pk = int(request.POST.get('tc')))
                    tester = User.objects.get(pk = int(request.POST.get('user')))
                    tr = TestCaseRun()
                    tr.test_case = tc
                    y = int(request.POST.get('year', ''))
                    m = int(request.POST.get('month', ''))
                    d = int(request.POST.get('day', ''))
                    tr.execution_date = datetime.date(y, m, d)
                    tr.tester = tester
                    tr.title = tc.title
                    tr.description = tc.description
                    tr.creation_date = tc.creation_date
                    tr.author = tc.author
                    tr.module = tc.module
                    tr.sub_module = tc.sub_module
                    tr.criticity = tc.criticity
                    tr.precondition = tc.precondition
                    tr.length = tc.length
                    tsrid = request.POST.get('tsr', '')
                    try:
                        parentTs = TestSetRun.objects.get(pk = int(tsrid))
                    except Exception:
                        parentTs = TestSetRun.objects.all()[0]
                        for t in TestSetRun.objects.filter(group = tester.groups.all()[0]):
                            if t.from_date < tr.execution_date:
                                parentTs = t
                                break
                        for t in TestSetRun.objects.filter(group = tester.groups.all()[0]):
                            if (t.from_date < tr.execution_date) and (parentTs.from_date < t.from_date):
                                parentTs = t
                    tr.test_set_run = parentTs
                    tr.status = 0
                    tr.save()
                    tr.make_step_runs()
                    tr.save()
                    try:
                        Availability.objects.get(day = tr.execution_date, user = tr.tester)
                    except Availability.DoesNotExist:
                        Availability(
                            day = tr.execution_date,
                            user = tr.tester,
                            group = tr.tester.groups.all()[0],
                        ).save()
                    logging.info("Test Case Run %s created in Test Set Run %s" % (tr.title, tr.test_set_run.name))
                    json = {'success': True}
                except Exception as detail:
                    logging.error("Unable to create test case run : %s" % detail)
                    json = {'success': False, 'errorMessage': 'could not create test case run'}
            elif action == 'delTcr':
                try:
                    tcr = TestCaseRun.objects.get(pk = int(request.POST.get('tcr', '')))
                    logging.info("Test Case Run %s deleted" % tcr.title)
                    tcr.delete()
                    json.append({'success': True})
                except Exception:
                    json.append({'success': False, 'errorMessage': 'could not delete test case run'})
            else:
                pass
        return HttpResponse(simplejson.dumps(json, default = dthandler))
    else:
        return HttpResponseRedirect('/')

def home(request):
    """
    test case set creation panel
    """
    json = []
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    if a_u.is_staff:
        if request.method == 'GET':
            try:
                action = request.GET.get('action', '')
            except Exception:
                pass
            if len(action) > 0:
                if action == 'testSets':
                    for tc in TestCase.objects.all().order_by('title'):
                        json.append({
                            'title': tc.title,
                            'id': tc.id,
                        })
                elif action == 'getTsTc':
                    try:
                        ts = TestSet.objects.get(pk = request.GET.get('tsid', ''))
                        for tc in ts.get_direct_test_cases():
                            json.append({
                                'title': tc.title,
                                'id': tc.id,
                            })
                    except Exception:
                        pass
                elif action == 'tcinfo':
                    try:
                        tc = TestCase.objects.get(pk = request.GET.get('tc', ''))
                        taglist = ''
                        for t in tc.get_tags():
                            taglist += t.name + ' '
                        json = {
                            'success': True,
                            'title': tc.title,
                            'description': tc.description,
                            'creation_date': tc.creation_date,
                            'author': tc.author.id,
                            'author_name': tc.author.username,
                            'module': tc.module,
                            'sub_module': tc.sub_module,
                            'criticity': tc.criticity,
                            'precondition': tc.precondition,
                            'length': tc.length,
                            'tags': taglist,
                        }
                        steps = []
                        for t in tc.get_steps():
                            if t.xp_image.name != '':
                                steps.append({
                                    'id': t.id,
                                    'num': t.num,
                                    'action': t.action,
                                    'expected': t.expected,
                                    'xp_image': t.xp_image._get_url(),
                                })
                            else:
                                steps.append({
                                    'id': t.id,
                                    'num': t.num,
                                    'action': t.action,
                                    'expected': t.expected,
                                    'xp_image': '',
                                })
                        json.update({'steps': steps})
                    except Exception as detail:
                        logging.error('failed to retrieve info : %s' % detail)
                        json = {'success': False}
                elif action == 'ispriv':
                    try:
                        u = User.objects.get(pk = request.GET.get('uid', ''))
                        json = {'success': True, 'priv': u.has_perm('test_manager.add_testcase')}
                    except Exception:
                        json = {'success': False}
                elif action == 'mainmenu':
                    json = config.main_menu
                elif action == 'teams':
                    for t in list(Group.objects.all().order_by('name')):
                        children = []
                        for u in list(t.user_set.all()):
                            children.append({'uid': u.id, 'text': u.username, 'leaf': True, 'iconCls': 'user'})
                        json.append({'leaf': False, 'gid': t.id, 'text': t.name, 'draggable': False, 'children': children, 'expanded': True, 'iconCls': 'team'})
                    for u in list(User.objects.all().order_by('username')):
                        if len(list(u.groups.all())) == 0:
                            json.append({'uid': u.id, 'text': u.username, 'leaf': True, 'iconCls': 'user'})
                elif action == 'testsets':
                    rts = list(TestSet.objects.filter(parent_test_set__id = 0).order_by('name'))
                    for ts in rts:
                        json.append(ts.build())
                    ots = list(TestCase.objects.all().order_by('title'))
                    for t in ots:
                        if len(t.test_sets.all()) == 0:
                            tags = []
                            for tag in t.get_tags():
                                tags.append(tag.name)
                            json.append({'tsid': 0, 'text': t.title, 'value': t.id, 'leaf': True, 'tags': tags, 'qtip': str(t.length) + ' min : ' + t.description})
                elif action == 'history':
                    tsrlist_u = list(TestSetRun.objects.all())
                    tsrlist = sorted(tsrlist_u, key = lambda s: s.from_date)
                    for s in tsrlist:
                        json.append({
                            'name': s.name,
                            'tsid': s.id,
                            'from': s.from_date,
                            'to': s.to_date,
                            'team': s.group.id,
                            'teamname': s.group.name,
                            'disp': s.displayed,
                        })
                elif action == 'getgroups':
                    for g in list(Group.objects.all().order_by('name')):
                        json.append({
                            'gid': g.id,
                            'gname': g.name,
                        })
                elif action == 'combotree':
                    json = config.get_tc_tree()
                elif action == 'combodata':
                    json = config.get_tc_data()
                else:
                    pass
            else:
                c = {}
                c.update(csrf(request))
                return render_to_response('manage/home.html', c)
        else:
            action = request.POST.get('action', '')
            if action == 'newtc':
                try:
                    tsid = request.POST.get('tsid', '')
                    title = request.POST.get('title', '').strip()
                    description = request.POST.get('description', '').strip()
                    precondition = request.POST.get('precondition', '').strip()
                    module = request.POST.get('module', '').strip()
                    modulev = unicodedata.normalize('NFKD', module.lower()).encode('ascii', 'ignore').replace(' ', '_')
                    smodule = request.POST.get('smodule', '').strip()
                    if len(title) * len(description) * len(precondition) * len(modulev) * len(smodule) == 0:
                        json = {'success': False, 'errorMessage': 'Please fill in all of the fields'}
                    else:
                        criticity = int(request.POST.get('criticity', ''))
                        duration = int(request.POST.get('duration', ''))
                        try:
                            Config.objects.get(ctype = 'module', name = module)
                        except Config.DoesNotExist:
                            c = Config(ctype = 'module', name = module, value = modulev)
                            c.save()
                        try:
                            Config.objects.get(ctype = modulev, name = smodule)
                        except Config.DoesNotExist:
                            c = Config(ctype = modulev, name = smodule, value = unicodedata.normalize('NFKD', smodule.lower()).encode('ascii', 'ignore').replace(' ', '_'))
                            c.save()
                        if criticity > 5:
                            criticity = 5
                        else:
                            pass
                        if criticity < 1:
                            criticity = 1
                        else:
                            pass
                        tc = TestCase(
                            title = title,
                            description = description,
                            author = User.objects.get(pk = request.session['uid']),
                            module = Config.objects.get(ctype = 'module', name = module).value,
                            sub_module = Config.objects.get(ctype = modulev, name = smodule).value,
                            criticity = criticity,
                            precondition = precondition,
                            length = duration,
                        )
                        tc.save()
                        logging.info("Test Case %s created" % tc.title)
                        tags = request.POST.get('tags', '').strip()
                        Tag(name = title, test_case = tc).save()
                        for tag in list(tags.split()):
                            Tag(name = tag, test_case = tc).save()
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
                                if l1 == 0:
                                    steps_remaining = False
                                else:
                                    n += 1
                            except (KeyError, TypeError):
                                steps_remaining = False
                        n -= 1
                        for i in range(n):
                            st = TestCaseStep(
                                num = i + 1,
                                action = request.POST.get('action' + str(i + 1), '').strip(),
                                expected = request.POST.get('expected' + str(i + 1), '').strip(),
                                test_case = tc,
                            )
                            if len(str(request.FILES.get('xp_image' + str(i + 1), ''))) > 0:
                                try:
                                    st.xp_image.delete()
                                except Exception:
                                    pass
                                st.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                            else:
                                pass
                            st.save()
                        json = {'success': True}
                except Exception as detail:
                    logging.error('could not create test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create test case'}
            elif action == 'newConfig':
                try:
                    cname = request.POST.get('configName', '')
                    curctype = request.POST.get('ctype', '')
                    cvalue = unicodedata.normalize('NFKD', cname.lower()).encode('ascii', 'ignore').replace(' ', '_')
                    if curctype == '__rootmods':
                        curctype = 'module'
                    else:
                        pass
                    Config(name = cname, ctype = curctype, value = cvalue).save()
                    logging.info('Created config option %s' % cname)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Could not add this Config Option : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Could not create this Config Option'}
            elif action == 'editConfig':
                try:
                    cname = request.POST.get('configName', '')
                    curctype = request.POST.get('ctype', '')
                    if curctype == '__rootmods':
                        curctype = 'module'
                        cvalue = unicodedata.normalize('NFKD', cname.lower()).encode('ascii', 'ignore').replace(' ', '_')
                        oldvalue = request.POST.get('oldvalue', '')
                        conf = Config.objects.get(value = oldvalue, ctype = curctype)
                        for subm in list(Config.objects.filter(ctype = oldvalue)):
                            subm.ctype = cvalue
                            subm.save()
                        conf.name = cname
                        conf.value = cvalue
                    else:
                        cvalue = unicodedata.normalize('NFKD', cname.lower()).encode('ascii', 'ignore').replace(' ', '_')
                        oldvalue = request.POST.get('oldvalue', '')
                        conf = Config.objects.get(value = oldvalue, ctype = curctype)
                        conf.name = cname
                        conf.value = cvalue
                    conf.save()
                    logging.info('Modified config option %s' % cname)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Could not edit this Config Option : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Could not modify this Config Option'}
            elif action == 'delConfig':
                try:
                    c = Config.objects.get(value = request.POST.get('item', ''))
                    if c.ctype == 'module':
                        for s in list(Config.objects.filter(ctype = c.value)):
                            s.delete()
                    else:
                        pass
                    c.delete()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Unable to delete Config Option : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Unable to delete this Config Option'}
            elif action == 'dealagain':
                try:
                    tsr = TestSetRun.objects.get(pk = int(request.POST.get('tsid', '')))
                    tsr.deal()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not deal again : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not deal again'}
            elif action == 'edittc':
                try:
                    tcid = int(request.POST.get('tcid', ''))
                    tsid = int(request.POST.get('tsid', ''))
                    tc = TestCase.objects.get(pk = tcid)
                    tc.title = request.POST.get('title', '').strip()
                    tc.description = request.POST.get('description', '').strip()
                    tc.precondition = request.POST.get('precondition', '').strip()
                    module = request.POST.get('module', '').strip()
                    modulev = unicodedata.normalize('NFKD', module.lower()).encode('ascii', 'ignore').replace(' ', '_')
                    smodule = request.POST.get('smodule', '').strip()
                    if len(tc.title) * len(tc.description) * len(tc.precondition) * len(modulev) * len(smodule) == 0:
                        json = {'success': False, 'errorMessage': 'Please fill in all of the fields'}
                    else:
                        try:
                            Config.objects.get(ctype = 'module', name = module)
                        except Config.DoesNotExist:
                            c = Config(ctype = 'module', name = module, value = modulev)
                            c.save()
                        try:
                            Config.objects.get(ctype = modulev, name = smodule)
                        except Config.DoesNotExist:
                            c = Config(ctype = modulev, name = smodule, value = unicodedata.normalize('NFKD', smodule.lower()).encode('ascii', 'ignore').replace(' ', '_'))
                            c.save()
                        tc.module = Config.objects.get(ctype = 'module', name = module).value
                        tc.sub_module = Config.objects.get(ctype = modulev, name = smodule).value
                        tc.criticity = int(request.POST.get('criticity', ''))
                        tc.length = int(request.POST.get('duration', ''))
                        tc.save()
                        logging.info("Test Case %s modified" % tc.title)
                        tags = request.POST.get('tags', '').strip()
                        Tag(name = tc.title, test_case = tc).save()
                        for tag in tc.get_tags():
                            tag.delete()
                        for tag in list(tags.split()):
                            Tag(name = tag, test_case = tc).save()
                        if tsid != -1:
                            ts = TestSet.objects.get(pk = tsid)
                            ts.test_cases.add(tc)
                            ts.save()
                        else:
                            pass
                        steps_remaining = True
                        old_tc = []
                        for step in tc.get_steps():
                            old_tc.append(step.id)
                        n = 1
                        while steps_remaining:
                            try:
                                l1 = len(request.POST.get('action' + str(n), ''))
                                if l1 == 0:
                                    steps_remaining = False
                                else:
                                    n += 1
                            except (KeyError, TypeError):
                                logging.info("exit")
                                steps_remaining = False
                        n -= 1
                        for i in range(n):
                            try:
                                st = TestCaseStep.objects.get(pk = int(request.POST.get('sid' + str(i + 1), '')))
                                old_tc.remove(st.id)
                                st.num = i + 1
                                st.action = request.POST.get('action' + str(i + 1), '').strip()
                                st.expected = request.POST.get('expected' + str(i + 1), '').strip()
                            except (TestCaseStep.DoesNotExist, ValueError):
                                st = TestCaseStep(
                                    num = i + 1,
                                    action = request.POST.get('action' + str(i + 1), '').strip(),
                                    expected = request.POST.get('expected' + str(i + 1), '').strip(),
                                    test_case = tc
                                )
                            if len(str(request.FILES.get('xp_image' + str(i + 1), ''))) > 0:
                                try:
                                    st.xp_image.delete()
                                except Exception:
                                    pass
                                st.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                            else:
                                pass
                            st.save()
                        for t in old_tc:
                            ts = TestCaseStep.objects.get(pk = t)
                            try:
                                ts.xp_image.delete()
                            except Exception:
                                pass
                            ts.delete()
                        json = {'success': True}
                except Exception as detail:
                    logging.error('Could not edit test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Could not edit test case'}
            elif action == 'editTs':
                try:
                    ts = TestSet.objects.get(pk = request.POST.get('tsid', ''))
                    test_set_name = request.POST.get('testSetName', '').strip()
                    if len(test_set_name) > 0:
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
                        ts.name = test_set_name
                        ts.parent_test_set_id = ptsi
                        ts.save()
                        logging.info("Test Set %s created" % ts.name)
                        for t in ts.get_direct_test_cases():
                            logging.info('removed %s from %s' % (t.title, ts.name))
                            ts.test_cases.remove(t)
                        for i in range(n):
                            logging.info('added %s to %s' % (TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))).title, ts.name))
                            ts.test_cases.add(TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))))
                        ts.save()
                        json = {'success': True}
                    else:
                        json = {'success': False, 'errorMessage': 'Please enter a valid text'}
                except Exception as detail:
                    logging.error('Could not edit Test Set : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not edit test set'}
            elif action == 'delts':
                try:
                    ts = TestSet.objects.get(pk=request.POST.get('ts', ''))
                    logging.info("Test Set %s deleted" % ts.name)
                    ts.delete()
                    json = {'success': True}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'could not delete test set'}
                    logging.error('could not delete test set : %s' % detail)
            elif action == 'delteam':
                try:
                    g = Group.objects.get(pk = request.POST.get('t', ''))
                    logging.info("Group %s deleted" % g.name)
                    g.delete()
                    json = {'success': True}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'could not delete team'}
                    logging.error('could not delete team : %s' % detail)
            elif action == 'deltc':
                try:
                    tc = TestCase.objects.get(pk = request.POST.get('tc', ''))
                    tsid = int(request.POST.get('ts', ''))
                    if tsid != -1:
                        # remove this test case from this test set
                        ts = TestSet.objects.get(pk = tsid)
                        ts.test_cases.remove(tc)
                        logging.info("Test Case %s deleted from %s" % (tc.title, ts.name))
                    else:
                        # permanently delete this test case
                        for s in tc.get_steps():
                            try:
                                s.xp_image.delete()
                            except Exception:
                                pass
                        tc.delete()
                        logging.info("Test Case %s deleted" % tc.title)
                    json = {'success': True}
                except Exception as detail:
                    logging.error("could not create test case %s" % detail)
                    json = {'success': False, 'errorMessage': 'could not delete test case'}
            elif action == 'deluser':
                try:
                    u = User.objects.get(pk = request.POST.get('u', ''))
                    if u.id != request.session['uid']:
                        logging.info("User %s deleted" % u.username)
                        u.delete()
                        json = {'success': True}
                    else:
                        json = {'success': False, 'errorMessage': 'User is authenticated'}
                except Exception as detail:
                    logging.error('could not delete user : %s' % detail)
                    json = {'success': False, 'errorMessage': 'An error occured'}
            elif action == 'mvts':
                try:
                    cts = TestSet.objects.get(pk = request.POST.get('cts', ''))
                    if request.POST.get('pts', '') == '-1':
                        cts.parent_test_set_id = 0
                        logging.info("Test Set %s moved to the root" % cts.name)
                    else:
                        cts.parent_test_set = TestSet.objects.get(pk = request.POST.get('pts', ''))
                        logging.info("Test Set %s moved inside of Test Set %s" % (cts.name, cts.parent_test_set.name))
                    cts.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move test set : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move test set'}
            elif action == 'mvtc':
                try:
                    tc = TestCase.objects.get(pk = request.POST.get('tc', ''))
                    if request.POST.get('tts', '') != '-1':
                        tts = TestSet.objects.get(pk = request.POST.get('tts', ''))
                        tts.test_cases.add(tc)
                        logging.info("Test Case %s added to Test Set %s" % (tc.title, tts.name))
                        tts.save()
                    else:
                        pass
                    if request.POST.get('fts', '') != '-1':
                        fts = TestSet.objects.get(pk = request.POST.get('fts', ''))
                        fts.test_cases.remove(tc)
                        logging.info('Test Case %s removed from Test Set %s' % (tc.title, fts.name))
                        fts.save()
                    else:
                        pass
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move test case'}
            elif action == 'cptc':
                try:
                    tc = TestCase.objects.get(pk = request.POST.get('tc', ''))
                    if request.POST.get('ts', '') != '-1':
                        ts = TestSet.objects.get(pk = request.POST.get('ts', ''))
                        ts.test_cases.add(tc)
                        ts.save()
                        logging.info("Test Case %s copied to Test Set %s" % (tc.title, ts.name))
                    else:
                        logging.info("Test Case %s cannot be copied to root" % tc.title)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not copy test case : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not copy test case'}
            elif action == 'mvuser':
                try:
                    u = User.objects.get(pk = request.POST.get('user', ''))
                    for g in u.groups.all():
                        u.groups.remove(g)
                    u.save()
                    gid = int(request.POST.get('team', ''))
                    if gid != -1:
                        g = Group.objects.get(pk = gid)
                        u.groups.add(g)
                        logging.info("User %s moved to %s" % (u.username, g.name))
                        u.save()
                    else:
                        logging.info("User %s moved out of groups" % u.username)
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not move user : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not move user'}
            elif action == 'chgdisp':
                try:
                    tsr = TestSetRun.objects.get(pk = int(request.POST.get('tsr', '')))
                    dispd = request.POST.get('disp', '')
                    if dispd == 'false':
                        tsr.displayed = False
                        logging.info("Test Set Run %s is now hidden" % tsr.name)
                    else:
                        tsr.displayed = True
                        logging.info("Test Set Run %s is now displayed" % tsr.name)
                    tsr.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not change test session status : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not change test session status'}
            elif action == 'newtestsetrun':
                try:
                    f_y = int(request.POST.get('from_y', ''))
                    f_m = int(request.POST.get('from_m', ''))
                    f_d = int(request.POST.get('from_d', ''))
                    t_y = int(request.POST.get('to_y', ''))
                    t_m = int(request.POST.get('to_m', ''))
                    t_d = int(request.POST.get('to_d', ''))
                    tsr = TestSetRun()
                    if len(request.POST.get('name', '').strip()) > 0:
                        tsr.name = request.POST.get('name', '').strip()
                        tsr.from_date = datetime.date(f_y, f_m, f_d)
                        tsr.to_date = datetime.date(t_y, t_m, t_d)
                        tsr.displayed = True
                        tsr.group = Group.objects.get(pk = int(request.POST.get('group', '')))
                        tsr.save()
                        logging.info("Test Set Run %s created" % tsr.name)
                        steps_remaining = True
                        n = 0
                        while steps_remaining:
                            try:
                                l1 = len(request.POST.get('tcid' + str(n), ''))
                                if l1 == 0:
                                    steps_remaining = False
                                else:
                                    pass
                                n += 1
                            except (KeyError, TypeError):
                                steps_remaining = False
                        test_cases = []
                        for i in range(n - 1):
                            test_cases.append(TestCase.objects.get(pk = int(request.POST.get('tcid' + str(i), ''))))
                        tsr.add_test_cases(test_cases)
                        usrs = list(tsr.group.user_set.all())
                        for nd in range((tsr.to_date - tsr.from_date).days + 1):
                            d = tsr.from_date + datetime.timedelta(nd)
                            for u in usrs:
                                try:
                                    a = Availability.objects.get(user = u, day = d)
                                    if(tsr.from_date + datetime.timedelta(nd)).weekday() > 4:
                                        a.delete()
                                except Availability.DoesNotExist:
                                    if d.weekday() < 5:
                                        a = Availability(user = u, day = d, group = tsr.group)
                                        a.save()
                        json = {'success': True}
                    else:
                        json = {'success': False, 'errorMessage': 'Please enter a valid text'}
                except Exception as detail:
                    logging.error('could not create test set run : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create test set run'}
            elif action == 'editUser':
                try:
                    u = User.objects.get(pk = request.POST.get('uid', ''))
                    if len(request.POST.get('username', '').strip()) > 0:
                        u.username = request.POST.get('username', '').strip()
                        u.save()
                        if u.is_staff:
                            pass
                        else:
                            is_priv = False
                            if request.POST.get('privileged', '') == 'on':
                                is_priv = True
                            special_permissions = [
                                'add_tag',
                                'change_tag',
                                'delete_tag',
                                'add_testcase',
                                'change_testcase',
                                'add_testcasestep',
                                'change_testcasestep',
                                'delete_testcasestep',
                                'add_testcaserun',
                                'add_testcasesteprun',
                                'delete_testcasesteprun',
                            ]
                            for p in special_permissions:
                                pm = Permission.objects.get(codename = p)
                                if is_priv:
                                    u.user_permissions.add(pm)
                                else:
                                    u.user_permissions.remove(pm)
                            u.save()
                        logging.info('User %s has been modified' % u.username)
                        json = {'success': True}
                    else:
                        json = {'success': False, 'errorMessage': 'Please enter a valid text'}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'Unable to modify this user'}
                    logging.error('Unable to edit user : %s' % detail)
            elif action == 'newUser':
                try:
                    user_name = request.POST.get('username', '').strip()
                    if len(user_name) > 0:
                        User(username = user_name).save()
                        u = User.objects.get(username = request.POST.get('username', '').strip())
                        logging.info("User %s created" % request.POST.get('username', '').strip())
                        if request.POST.get('team', '') != '-1':
                            g = Group.objects.get(pk = request.POST.get('team', ''))
                            u.groups.add(g)
                            privileged = request.POST.get('privileged', '')
                            permissions = [
                                'change_availability',
                                'add_jira',
                                'change_jira',
                                'change_testcaserun',
                                'change_testcasesteprun',
                            ]
                            if privileged == 'on':
                                permissions.extend([
                                    'add_tag',
                                    'change_tag',
                                    'delete_tag',
                                    'add_testcase',
                                    'change_testcase',
                                    'add_testcasestep',
                                    'change_testcasestep',
                                    'delete_testcasestep',
                                    'add_testcaserun',
                                    'add_testcasesteprun',
                                    'delete_testcasesteprun',
                                ])
                            else:
                                pass
                            for p in permissions:
                                pm = Permission.objects.get(codename = p)
                                u.user_permissions.add(pm)
                            u.save()
                        else:
                            pass
                        json = {'success': True}
                    else:
                        json = {'success': False, 'errorMessage': 'Enter a valid name'}
                except Exception as detail:
                    logging.error('could not create user : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create user'}
            elif action == 'newTeam':
                try:
                    if len(request.POST.get('name', '').strip()) > 0:
                        g = Group(name = request.POST.get('name', '').strip())
                        g.save()
                        logging.info("Group %s created" % g.name)
                        json = {'success': True}
                    else:
                        json = {'success': False, 'errorMessage': 'Enter a valid name'}
                except Exception as detail:
                    logging.error('could not create team : %s' % detail)
                    json = {'success': False, 'errorMessage': 'could not create team'}
            elif action == 'testSets':
                try:
                    test_set_name = request.POST.get('testSetName', '').strip()
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
                    logging.info("Test Set %s created" % ts.name)
                    for i in range(n):
                        ts.test_cases.add(TestCase.objects.get(pk = int(request.POST.get('tc' + str(i), ''))))
                    ts.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('could not create test set : %s' % detail)
                    json = {'success': False, 'errorMessage': 'The test set couldn\'t be created'}
            else:
                pass
        return HttpResponse(simplejson.dumps(json, default = dthandler))
    else:
        return HttpResponseRedirect('/')

def planning(request):
    """
        planning page (main page for testers)
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if request.method == 'GET':
        try:
            action = request.GET.get('action', '')
            if action == 'events':
                tcr = TestCaseRun.objects.filter(tester = request.session['uid']).order_by('id')
                json = []
                dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
                for t in tcr:
                    json.append({
                        'title': t.title,
                        'execution_date': t.execution_date,
                        'tcrid': t.id,
                        'status': t.status,
                    })
                return HttpResponse(simplejson.dumps(json, default=dthandler))
            else:
                pass
        except Exception:
            pass
        c = Context({'tester_visa': u.username.upper(), 'tester_id': u.id, 'tester_priv': u.has_perm('test_manager.add_testcase')})
        c.update(csrf(request))
        return render_to_response('test_manager/planning.html', c)
    else:
        if u.has_perm('test_manager.add_testcaserun'):
            try:
                tcr = TestCaseRun.objects.get(pk = request.POST.get('tcr', ''))
                tcr.execution_date = datetime.date(int(request.POST.get('year', '')), int(request.POST.get('month', '')), int(request.POST.get('day', '')))
                tcr.save()
                logging.info("Test Case Run %s moved to %s" % (tcr.title, tcr.execution_date.isoformat()))
                json = {'success': True}
            except Exception as detail:
                logging.error('could not move test case run : %s' % detail)
                json = {'success': False, 'errorMessage': 'could not move test case run'}
        else:
            logging.error('user %s attempted to move test case run' % u.username)
            json = {'success': False, 'errorMessage': 'You are not allowed to do this'}
        return HttpResponse(simplejson.dumps(json))

def availabilities(request):
    """
        a page to save one's own availabilities
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    u = User.objects.get(pk = request.session['uid'])
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
    if request.method == 'GET':
        action = request.GET.get('action', '')
        if len(action) > 0:
            json = []
            if action == 'avails':
                avs = Availability.objects.filter(user = u)
                for a in avs:
                    json.append({
                        'pct': a.avail,
                        'title': str(a.avail) + ' %',
                        'execution_date': a.day,
                        'tcrid': a.id,
                    })
            else:
                pass
            return HttpResponse(simplejson.dumps(json, default = dthandler))
        else:
            c = Context({'tester_visa': u.username.upper(), 'tester_id': u.id, 'tester_priv': u.has_perm('test_manager.add_testcase')})
            c.update(csrf(request))
            return render_to_response('test_manager/availabilities.html', c)
    else:
        action = request.POST.get('action', '')
        json = []
        if action == 'chgavail':
            try:
                y = int(request.POST.get('y', ''))
                m = int(request.POST.get('m', ''))
                d = int(request.POST.get('d', ''))
                pct = int(request.POST.get('pct', ''))
                a_day = datetime.date(y, m, d)
                a = Availability.objects.get(user = u, day = a_day)
                logging.info('User %s changed availability for %r from %d to %d' % (u.username, a_day, a.avail, pct))
                a.avail = pct
                a.save()
                json = {'success': True}
            except Exception as detail:
                json = {'success': False, 'errorMessage': 'Could not change availability'}
                logging.error('User could not change availability : %s' % detail)
        else:
            pass
        return HttpResponse(simplejson.dumps(json))

def create_tc(request):
    """
        test case creation page
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if a_u.has_perm('test_manager.add_testcase'):
        if request.method == 'GET':
            try:
                action = request.GET.get('action', '')
                if action == 'comboData':
                    return HttpResponse(simplejson.dumps(config.get_tc_data()))
                else:
                    pass
            except Exception:
                pass
            c = {'tester_visa': User.objects.get(pk = request.session['uid']).username.upper()}
            c.update(csrf(request))
            return render_to_response('test_manager/create_tc.html', c)
        else:
            try:
                title = request.POST.get('title', '').strip()
                description = request.POST.get('description', '').strip()
                precondition = request.POST.get('precondition', '').strip()
                module = request.POST.get('module', '').strip()
                modulev = unicodedata.normalize('NFKD', module.lower()).encode('ascii', 'ignore').replace(' ', '_')
                smodule = request.POST.get('smodule', '').strip()
                criticity = int(request.POST.get('criticity', ''))
                duration = int(request.POST.get('duration', ''))
                if criticity > 5:
                    criticity = 5
                else:
                    pass
                if criticity < 1:
                    criticity = 1
                else:
                    pass
                try:
                    Config.objects.get(ctype = 'module', name = module)
                except Config.DoesNotExist:
                    c = Config(ctype = 'module', name = module, value = modulev)
                    c.save()
                try:
                    Config.objects.get(ctype = modulev, name = smodule)
                except Config.DoesNotExist:
                    c = Config(ctype = modulev, name = smodule, value = unicodedata.normalize('NFKD', smodule.lower()).encode('ascii', 'ignore').replace(' ', '_'))
                    c.save()
                tc = TestCase(title = title,
                    description = description,
                    author = User.objects.get(pk = request.session['uid']),
                    module = Config.objects.get(ctype = 'module', name = module).value,
                    sub_module = Config.objects.get(ctype = modulev, name = smodule).value,
                    criticity = criticity,
                    precondition = precondition,
                    length = duration,
                )
                tc.save()
                logging.info("Test Case %s created" % tc.title)
                Tag(name = title, test_case = tc).save()
                tags = request.POST.get('tags', '').strip()
                for tag in list(tags.split()):
                    Tag(name = tag, test_case = tc).save()
                steps_remaining = True
                n = 1
                while steps_remaining:
                    try:
                        l1 = len(request.POST.get('action' + str(n), ''))
                        if l1 == 0:
                            steps_remaining = False
                        else:
                            pass
                        n += 1
                    except (KeyError, TypeError):
                        steps_remaining = False
                n -= 2
                for i in range(n):
                    st = TestCaseStep(
                        num = i + 1,
                        action = request.POST.get('action' + str(i + 1), '').strip(),
                        expected = request.POST.get('expected' + str(i + 1), '').strip(),
                        test_case = tc,
                    )
                    if len(str(request.FILES.get('xp_image' + str(i + 1), ''))) > 0:
                        try:
                            st.xp_image.delete()
                        except Exception:
                            pass
                        st.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                    else:
                        pass
                    st.save()
                return HttpResponse(simplejson.dumps({'success': True}))
            except Exception as detail:
                logging.error('could not create test case : %s' % detail)
                return HttpResponse(simplejson.dumps({'success': False, 'errorMessage': 'could not create test case'}))
    else:
        logging.info('User %s attempted to access the create_tc page' % u.username)
        return HttpResponseRedirect('/test_manager/')

def view_hist(request):
    """
        Controller for the history page (view old test case runs)
    """
    try:
        a_u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if a_u.is_staff:
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        if request.method == 'GET':
            action = request.GET.get('action', '')
            if len(action) == 0:
                tcrid = int(request.GET.get('tcrid', ''))
                return render_to_response('manage/view_hist.html', {'tcrid': tcrid})
            else:
                json = []
                if action == 'tcrinfo':
                    try:
                        tcr = TestCaseRun.objects.get(pk = int(request.GET.get('tcrid', '')))
                        tags = ''
                        for t in tcr.get_tags():
                            tags += t.__unicode__() + ' '
                        json = {
                            'tctitle': tcr.title,
                            'description': tcr.description,
                            'precondition': tcr.precondition,
                            'module': Config.objects.get(value = tcr.module, ctype = 'module').name,
                            'sub_module': Config.objects.get(value = tcr.sub_module, ctype = tcr.module).name,
                            'environment': tcr.environment,
                            'os': tcr.os,
                            'browser': tcr.browser,
                            'release': tcr.release,
                            'version': tcr.version,
                            'criticity': tcr.criticity,
                            'tags': tags,
                            'duration': tcr.length,
                            'tester': tcr.tester.username,
                            'ex_date': tcr.execution_date.isoformat(),
                            'success': True,
                            'steps': [],
                        }
                        for s in tcr.get_steps():
                            jiras = []
                            for j in s.get_jiras():
                                jiras.append(j.name)
                            try:
                                xp_image_url = s.xp_image._get_url()
                            except Exception:
                                xp_image_url = ''
                            json['steps'].append({
                                'num': s.num,
                                'action': s.action,
                                'expected': s.expected,
                                'jiras': jiras,
                                'done': s.done,
                                'status': s.status,
                                'comment': s.comment,
                                'xp_image': xp_image_url,
                            })
                    except Exception as detail:
                        logging.error('Unable to retrieve info : %s' % detail)
                        json = {'success': False, 'errorMessage': 'Unable to retrieve info'}
                else:
                    pass
                return HttpResponse(simplejson.dumps(json))
        else:
            return HttpResponse(None)
    else:
        return HttpResponseRedirect('/')

def do_test(request):
    """
        Controller for the test execution page
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if request.method == 'GET':
        action = request.GET.get('action', '')
        if len(action) == 0:
            try:
                tc = TestCaseRun.objects.get(pk = int(request.GET.get('t', '')))
                request.session['ctcr'] = tc.id
                c = Context({'t': tc.id, 'tester_visa': u.username.upper(), 'tester_id': u.id, 'tester_priv': u.has_perm('test_manager.add_testcase')})
                c.update(csrf(request))
                return render_to_response('test_manager/do_test.html', c)
            except Exception as detail:
                logging.error('could not find test set run : %s' % detail)
                return HttpResponse('erreur...')
        else:
            json = []
            dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
            try:
                tcr = TestCaseRun.objects.get(pk = request.session['ctcr'])
                if tcr.tester_id != request.session['uid']:
                    json = {'success': False, 'errorMessage': 'This test case run was given to another tester'}
                else:
                    if action == 'tcrinfo':
                        try:
                            module = Config.objects.get(ctype = 'module', value = tcr.module).name
                        except Config.DoesNotExist:
                            module = tcr.module
                        try:
                            sub_module = Config.objects.get(ctype = tcr.module, value = tcr.sub_module).name
                        except Config.DoesNotExist:
                            sub_module = tcr.sub_module
                        soap_client = Client(jira_server_url)
                        auth = request.session['auth']
                        statuses = soap_client.service.getStatuses(auth)
                        id2statuses = {}
                        for s in statuses:
                            id2statuses[s.id] = s
                        os = []
                        for o in list(Config.objects.filter(ctype = 'os')):
                            os.append({'name': o.name, 'value': o.value})
                        envir = []
                        for o in list(Config.objects.filter(ctype = 'envir')):
                            envir.append({'name': o.name, 'value': o.value})
                        browser = []
                        for o in list(Config.objects.filter(ctype = 'browser')):
                            browser.append({'name': o.name, 'value': o.value})
                        release = []
                        for o in list(Config.objects.filter(ctype = 'release')):
                            release.append({'name': o.name, 'value': o.value})
                        version = []
                        for o in list(Config.objects.filter(ctype = 'version')):
                            version.append({'name': o.name, 'value': o.value})
                        tags = []
                        for o in tcr.get_tags():
                            tags.append(o.name)
                        steps = []
                        for o in tcr.get_steps():
                            jiras = []
                            for j in o.get_jiras():
                                try:
                                    jira_status = soap_client.service.getIssue(auth, j.name).status
                                    jiras.append({
                                        'name': j.name,
                                        'status': id2statuses[jira_status].name,
                                        'icon': id2statuses[jira_status].icon,
                                    })
                                except Exception:
                                    jiras.append({
                                        'name': j.name,
                                        'status': '',
                                        'icon': '',
                                    })
                            try:
                                xp_image_url = o.xp_image._get_url()
                            except Exception:
                                xp_image_url = ''
                            to_append = {
                                'id': o.id,
                                'num': o.num,
                                'action': o.action,
                                'expected': o.expected,
                                'xp_image': xp_image_url,
                                'comment': o.comment,
                                'jiras': jiras,
                            }
                            if o.done:
                                to_append.update({'status': o.status})
                            else:
                                to_append.update({'status': 'undefined'})
                            steps.append(to_append)
                        tc = {
                            'precondition': tcr.precondition,
                            'module': module,
                            'creation_date': tcr.creation_date,
                            'status': tcr.status,
                            'title': tcr.title,
                            'execution_date': tcr.execution_date,
                            'environment': tcr.environment,
                            'version': tcr.version,
                            'description': tcr.description,
                            'criticity': tcr.criticity,
                            'sub_module': sub_module,
                            'length': tcr.length,
                            'release': tcr.release,
                            'author': tcr.author_id,
                            'os': tcr.os,
                            'browser': tcr.browser,
                            'tags': tags,
                            'steps': steps,
                        }
                        json = {
                            'success': True,
                            'tc': tc,
                            'config': {
                                'os': os,
                                'envir': envir,
                                'browser': browser,
                                'release': release,
                                'version': version,
                            },
                        }
                    elif action == 'edittcrdata':
                        combos = config.get_tc_data()


                        taglist = ''
                        for t in tcr.get_tags():
                            taglist += t.name + ' '
                        tcinfo = {
                            'success': True,
                            'title': tcr.title,
                            'description': tcr.description,
                            'creation_date': tcr.creation_date,
                            'author': tcr.author.id,
                            'author_name': tcr.author.username,
                            'module': tcr.module,
                            'sub_module': tcr.sub_module,
                            'criticity': tcr.criticity,
                            'precondition': tcr.precondition,
                            'length': tcr.length,
                            'tags': taglist,
                        }
                        steps = []
                        for t in tcr.get_steps():
                            if t.xp_image.name != '':
                                steps.append({
                                    'id': t.id,
                                    'num': t.num,
                                    'action': t.action,
                                    'expected': t.expected,
                                    'xp_image': t.xp_image._get_url(),
                                })
                            else:
                                steps.append({
                                    'id': t.id,
                                    'num': t.num,
                                    'action': t.action,
                                    'expected': t.expected,
                                    'xp_image': '',
                                })
                        tcinfo.update({'steps': steps})

                        modules = []
                        submodules = {}
                        for o in list(Config.objects.filter(ctype = 'module')):
                            modules.append({'name': o.name, 'value': o.value})
                            sub_modules = []
                            for s in list(Config.objects.filter(ctype = o.value)):
                                sub_modules.append({'name': s.name, 'value': s.value})
                            submodules.update({o.value: sub_modules})

                        json = {'submodules': submodules, 'module': modules, 'tcr': tcinfo, 'smodule': [{'name': 'Choose a module first !', 'value': None}]}



                    else:
                        json = {'success': False, 'errorMessage': 'wrong request'}
            except Exception as detail:
                logging.error('could not retrieve test case run info : %s' % detail)
                json = {'success': False, 'errorMessage': 'could not retrieve test case run info'}
            return HttpResponse(simplejson.dumps(json, default = dthandler))
    elif request.method == 'POST':
        json = []
        action = request.POST.get('action', '')
        if action == 'setstatus':
            try:
                sid = TestCaseStepRun.objects.get(pk = int(request.POST.get('sid', '')))
                tcr = sid.test_case
                if tcr.status == 0:
                    tcr.status = 1
                    tcr.save()
                else:
                    pass
                is_ok = True
                log_msg = 'OK'
                if request.POST.get('is_ok', '') == 'false':
                    is_ok = False
                    log_msg = 'KO'
                    if tcr.status < 2:
                        tcr.status = 2
                        tcr.save()
                    else:
                        pass
                sid.status = is_ok
                sid.done = True
                sid.save()
                logging.info('Step Run "%s" is %s' % (sid, log_msg))
                tcr = sid.test_case
                finished = False
                if len(tcr.os) * len(tcr.version) * len(tcr.environment) * len(tcr.release) * len(tcr.browser) > 0:
                    finished = True
                    all_ok = True
                    for s in tcr.get_steps():
                        finished &= s.done
                        all_ok &= s.status
                    if(finished):
                        if(all_ok):
                            tcr.status = 4
                        else:
                            tcr.status = 3
                        tcr.save()
                    else:
                        pass
                else:
                    pass
                json = {'success': True, 'over': finished}
            except Exception as detail:
                json = {'success': False, 'errorMessage': 'could not change test step status'}
                logging.error('Could not change test case step run status : %s' % detail)
        elif action == 'edittcr':
            try:
                tcr = TestCaseRun.objects.get(pk = int(request.session['ctcr']))
                tc = tcr.test_case
                tc.title = request.POST.get('title', '').strip()
                tc.description = request.POST.get('description', '').strip()
                tc.precondition = request.POST.get('precondition', '').strip()
                tcr.title = request.POST.get('title', '').strip()
                tcr.description = request.POST.get('description', '').strip()
                tcr.precondition = request.POST.get('precondition', '').strip()
                module = request.POST.get('module', '').strip()
                modulev = unicodedata.normalize('NFKD', module.lower()).encode('ascii', 'ignore').replace(' ', '_')
                smodule = request.POST.get('smodule', '').strip()
                try:
                    Config.objects.get(ctype = 'module', name = module)
                except Config.DoesNotExist:
                    c = Config(ctype = 'module', name = module, value = modulev)
                    c.save()
                try:
                    Config.objects.get(ctype = modulev, name = smodule)
                except Config.DoesNotExist:
                    c = Config(ctype = modulev, name = smodule, value = unicodedata.normalize('NFKD', smodule.lower()).encode('ascii', 'ignore').replace(' ', '_'))
                    c.save()
                tc.module = Config.objects.get(ctype = 'module', name = module).value
                tc.sub_module = Config.objects.get(ctype = modulev, name = smodule).value
                tc.criticity = int(request.POST.get('criticity', ''))
                tc.length = int(request.POST.get('duration', ''))
                tc.save()
                tcr.module = Config.objects.get(ctype = 'module', name = module).value
                tcr.sub_module = Config.objects.get(ctype = modulev, name = smodule).value
                tcr.criticity = int(request.POST.get('criticity', ''))
                tcr.length = int(request.POST.get('duration', ''))
                tcr.save()
                logging.info("Test Case %s modified" % tc.title)
                logging.info("Test Case Run %s modified" % tcr.title)
                tags = request.POST.get('tags', '').strip()
                Tag(name = tc.title, test_case = tc).save()
                for tag in tc.get_tags():
                    tag.delete()
                for tag in list(tags.split()):
                    Tag(name = tag, test_case = tc).save()
                steps_remaining = True
                old_tc = []
                old_tcr = []
                for step in tcr.get_steps():
                    old_tc.append(step.test_case_step.id)
                    old_tcr.append(step.id)
                n = 1
                while steps_remaining:
                    try:
                        l1 = len(request.POST.get('action' + str(n), ''))
                        if l1 == 0:
                            steps_remaining = False
                        else:
                            n += 1
                    except (KeyError, TypeError):
                        steps_remaining = False
                n -= 1
                for i in range(n):
                    try:
                        strun = TestCaseStepRun.objects.get(pk = int(request.POST.get('sid' + str(i + 1), '')))
                        st = strun.test_case_step
                        old_tcr.remove(strun.id)
                        old_tc.remove(st.id)
                        st.num = i + 1
                        st.action = request.POST.get('action' + str(i + 1), '').strip()
                        st.expected = request.POST.get('expected' + str(i + 1), '').strip()
                        strun.num = i + 1
                        strun.action = request.POST.get('action' + str(i + 1), '').strip()
                        strun.expected = request.POST.get('expected' + str(i + 1), '').strip()
                    except (TestCaseStep.DoesNotExist, TestCaseStepRun.DoesNotExist, ValueError):
                        st = TestCaseStep(
                            num = i + 1,
                            action = request.POST.get('action' + str(i + 1), '').strip(),
                            expected = request.POST.get('expected' + str(i + 1), '').strip(),
                            test_case = tc,
                        )
                        st.save()
                        strun = TestCaseStepRun(
                            num = i + 1,
                            action = request.POST.get('action' + str(i + 1), '').strip(),
                            expected = request.POST.get('expected' + str(i + 1), '').strip(),
                            test_case = tcr,
                            test_case_step = st,
                        )
                        strun.save()
                    if len(str(request.FILES.get('xp_image' + str(i + 1), ''))) > 0:
                        try:
                            st.xp_image.delete()
                        except Exception:
                            pass
                        try:
                            strun.xp_image.delete()
                        except Exception:
                            pass
                        st.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                        strun.xp_image = request.FILES.get('xp_image' + str(i + 1), '')
                    else:
                        pass
                    st.save()
                    strun.save()
                for t in old_tc:
                    ts = TestCaseStep.objects.get(pk = t)
                    try:
                        ts.xp_image.delete()
                    except Exception:
                        pass
                    ts.delete()
                json = {'success': True}
            except Exception as detail:
                logging.error('Could not modify the test case : %s' % detail)
                json = {'success': False, 'errorMessage': 'Could not modify the test case'}
        elif action == 'newjira':
            try:
                tsr = TestCaseStepRun.objects.get(pk = int(request.POST.get('tsrid', '')))
                Jira(test_case_step = tsr, name = request.POST.get('jiraref').strip().upper()).save()
                json = {'success': True}
            except Exception as detail:
                logging.error('Could not add jira : %s' % detail)
                json = {'success': False, 'errorMessage': 'Could not create Jira'}
        elif action == 'settcrparam':
            try:
                my_ctype = request.POST.get('param', '').strip()
                my_value = request.POST.get('value', '').strip()
                try:
                    param = Config.objects.get(ctype = my_ctype, value = my_value)
                except Config.DoesNotExist:
                    param = Config(
                        ctype = my_ctype,
                        value = my_value.lower().encode('ascii', 'ignore').replace(' ', '_'),
                        name = my_value,
                    )
                    param.save()
                tcr = TestCaseRun.objects.get(pk = int(request.session['ctcr']))
                if tcr.status == 0:
                    tcr.status = 1
                    tcr.save()
                else:
                    pass
                if my_ctype == 'os':
                    tcr.os = param.value
                elif my_ctype == 'version':
                    tcr.version = param.value
                elif my_ctype == 'envir':
                    tcr.environment = param.value
                elif my_ctype == 'release':
                    tcr.release = param.value
                elif my_ctype == 'browser':
                    tcr.browser = param.value
                else:
                    pass
                tcr.save()
                finished = False
                if len(tcr.os) * len(tcr.version) * len(tcr.environment) * len(tcr.release) * len(tcr.browser) > 0:
                    finished = True
                    all_ok = True
                    for s in tcr.get_steps():
                        finished &= s.done
                        all_ok &= s.status
                    if(finished):
                        if(all_ok):
                            tcr.status = 4
                        else:
                            tcr.status = 3
                        tcr.save()
                    else:
                        pass
                else:
                    pass
                json = {'success': True, 'over': finished}
                logging.info('tcr %s : Set attribute %s to %s' % (tcr.__unicode__(), my_ctype, my_value))
            except Exception as detail:
                logging.error('Could not set this parameter : %s' % detail)
                json = {'error': True, 'errorMessage': 'Could not set this parameter'}
        elif action == 'addcomment':
            try:
                sid = TestCaseStepRun.objects.get(pk = int(request.POST.get('sid', '')))
                comment = request.POST.get('comment', '').strip()
                sid.comment = comment
                sid.save()
                json = {'success': True}
            except Exception as detail:
                logging.error('Could not add comment : %s' % detail)
                json = {'success': False, 'errorMessage': 'Could not edit the comment for this step'}
        else:
            pass
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponse('erreur...')

def monitoring(request):
    """
        Controller for the "monitoring" page
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if request.method == 'GET':
        action = request.GET.get('action', '')
        if len(action) == 0:
            c = Context({'tester_visa': u.username.upper(), 'tester_id': u.id, 'tester_priv': u.has_perm('test_manager.add_testcase')})
            c.update(csrf(request))
            return render_to_response('test_manager/monitoring.html', c)
        else:
            if action == 'monitoring':
                try:
                    today = datetime.date.today()
                    repart_d = [{
                        'name': 'Not started',
                        'value': 0,
                    }, {
                        'name': 'Started without error',
                        'value': 0,
                    }, {
                        'name': 'Started with error(s)',
                        'value': 0,
                    }, {
                        'name': 'Completed with error(s)',
                        'value': 0,
                    }, {
                        'name': 'Completed without errors',
                        'value': 0,
                    }]
                    repart_w = [{
                        'name': 'Not started',
                        'value': 0,
                    }, {
                        'name': 'Started',
                        'value': 0,
                    }, {
                        'name': 'Errors',
                        'value': 0,
                    }, {
                        'name': 'Completed with error(s)',
                        'value': 0,
                    }, {
                        'name': 'Completed without errors',
                        'value': 0,
                    }]
                    repart_s = [{
                        'name': 'Not started',
                        'value': 0,
                    }, {
                        'name': 'Started',
                        'value': 0,
                    }, {
                        'name': 'Errors',
                        'value': 0,
                    }, {
                        'name': 'Completed with error(s)',
                        'value': 0,
                    }, {
                        'name': 'Completed without errors',
                        'value': 0,
                    }]
                    progress = [{
                        'name': 'Today',
                        'value': 0,
                        'expected': 0,
                    }, {
                        'name': 'Week',
                        'value': 0,
                        'expected': 0,
                    }, {
                        'name': 'Session',
                        'value': 0,
                        'expected': 0,
                    }]
                    session = TestSetRun.objects.get(pk = int(request.GET.get('tsid', '')))
                    tc_t = TestCaseRun.objects.filter(execution_date = today, test_set_run = session)
                    monday = today - datetime.timedelta(today.isoweekday() - 1)
                    friday = today + datetime.timedelta(5 - today.isoweekday())
                    tc_w = TestCaseRun.objects.filter(execution_date__gte = monday, execution_date__lte = friday, test_set_run = session)
                    tc_s = TestCaseRun.objects.filter(test_set_run = session)
                    for t in tc_t:
                        repart_d[t.status]['value'] += 1
                        progress[0]['expected'] += 1
                        if t.status > 2:
                            progress[0]['value'] += 1
                        elif t.status == 2:
                            c_s = 0
                            for st in t.get_steps():
                                if c_s == 0:
                                    if st.done == False:
                                        c_s = -1
                                    else:
                                        if st.status != True:
                                            c_s = 1
                                        else:
                                            pass
                                elif c_s == 1:
                                    if st.done == False:
                                        c_s = 2
                                    else:
                                        c_s = -1
                                elif c_s == 2:
                                    if st.done == True:
                                        c_s = -1
                                    else:
                                        pass
                                else:
                                    pass
                            if c_s == 2:
                                progress[0]['value'] += 1
                            else:
                                pass
                        else:
                            pass
                    for t in tc_w:
                        repart_w[t.status]['value'] += 1
                        if t.execution_date <= today:
                            progress[1]['expected'] += 1
                        else:
                            pass
                        if t.status > 2:
                            progress[1]['value'] += 1
                        elif t.status == 2:
                            c_s = 0
                            for st in t.get_steps():
                                if c_s == 0:
                                    if st.done == False:
                                        c_s = -1
                                    else:
                                        if st.status != True:
                                            c_s = 1
                                        else:
                                            pass
                                elif c_s == 1:
                                    if st.done == False:
                                        c_s = 2
                                    else:
                                        c_s = -1
                                elif c_s == 2:
                                    if st.done == True:
                                        c_s = -1
                                    else:
                                        pass
                                else:
                                    pass
                            if c_s == 2:
                                progress[1]['value'] += 1
                            else:
                                pass
                        else:
                            pass
                    for t in tc_s:
                        repart_s[t.status]['value'] += 1
                        if t.execution_date <= today:
                            progress[2]['expected'] += 1
                        else:
                            pass
                        if t.status > 2:
                            progress[2]['value'] += 1
                        elif t.status == 2:
                            c_s = 0
                            for st in t.get_steps():
                                if c_s == 0:
                                    if st.done == False:
                                        c_s = -1
                                    else:
                                        if st.status != True:
                                            c_s = 1
                                        else:
                                            pass
                                elif c_s == 1:
                                    if st.done == False:
                                        c_s = 2
                                    else:
                                        c_s = -1
                                elif c_s == 2:
                                    if st.done == True:
                                        c_s = -1
                                    else:
                                        pass
                                else:
                                    pass
                            if c_s == 2:
                                progress[2]['value'] += 1
                            else:
                                pass
                        else:
                            pass
                    json = {'success': True, 'progress': progress, 'repart_d': repart_d, 'repart_w': repart_w, 'repart_s': repart_s}
                except Exception as detail:
                    json = {'success': False, 'errorMessage': 'Could not retrieve statistics'}
                    logging.error('Could not retrieve statistics : %s' % detail)
            elif action == 'get_sess':
                json = []
                for s in TestSetRun.objects.all().order_by('name'):
                    json.append({'name': s.name, 'value': s.id})
            else:
                json = {'success': False, 'errorMessage': 'Wrong request'}
            return HttpResponse(simplejson.dumps(json))


def config_opts(request):
    """
        Controller for the "configuration" page
    """
    try:
        u = User.objects.get(pk = request.session['uid'])
    except KeyError:
        logout(request)
        return HttpResponseRedirect('/login/')
    if u.has_perm('test_manager.add_testcaserun'):
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else None
        if request.method == 'GET':
            action = request.GET.get('action', '')
            if len(action) == 0:
                c = Context({'tester_visa': u.username.upper()})
                c.update(csrf(request))
                return render_to_response('test_manager/config_opts.html', c)
            else:
                json = []
                if action == 'combotree':
                    json = config.get_tc_tree()
                else:
                    pass
                return HttpResponse(simplejson.dumps(json))
        else:
            json = []
            action = request.POST.get('action', '')
            if action == 'newConfig':
                try:
                    cname = request.POST.get('configName', '')
                    curctype = request.POST.get('ctype', '')
                    cvalue = unicodedata.normalize('NFKD', cname.lower()).encode('ascii', 'ignore').replace(' ', '_')
                    if curctype == '__rootmods':
                        curctype = 'module'
                    else:
                        pass
                    Config(name = cname, ctype = curctype, value = cvalue).save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Unable to create this Config Option : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Unable to create this Config Option'}
            elif action == 'editConfig':
                try:
                    cname = request.POST.get('configName', '')
                    curctype = request.POST.get('ctype', '')
                    if curctype == '__rootmods':
                        curctype = 'module'
                        cvalue = unicodedata.normalize('NFKD', cname.lower()).encode('ascii', 'ignore').replace(' ', '_')
                        oldvalue = request.POST.get('oldvalue', '')
                        conf = Config.objects.get(value = oldvalue, ctype = curctype)
                        for subm in list(Config.objects.filter(ctype = oldvalue)):
                            subm.ctype = cvalue
                            subm.save()
                        conf.name = cname
                        conf.value = cvalue
                    else:
                        cvalue = unicodedata.normalize('NFKD', cname.lower()).encode('ascii', 'ignore').replace(' ', '_')
                        oldvalue = request.POST.get('oldvalue', '')
                        conf = Config.objects.get(value = oldvalue, ctype = curctype)
                        conf.name = cname
                        conf.value = cvalue
                    conf.save()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Unable to edit this Config Option : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Unable to edit this Config Option'}
            elif action == 'delConfig':
                try:
                    c = Config.objects.get(value = request.POST.get('item', ''))
                    if c.ctype == 'module':
                        for s in list(Config.objects.filter(ctype = c.value)):
                            s.delete()
                    else:
                        pass
                    c.delete()
                    json = {'success': True}
                except Exception as detail:
                    logging.error('Unable to delete this Config Option : %s' % detail)
                    json = {'success': False, 'errorMessage': 'Unable to delete this Config Option'}
            else:
                pass
            return HttpResponse(simplejson.dumps(json))
    else:
        logging.info('User %s attempted to access the config_opts page' % u.username)
        return HttpResponseRedirect('/test_manager/')
