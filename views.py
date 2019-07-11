from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from Eventak.models import events, Users, Reservations, EventTypes, UserEvent, RelStat
from .forms import *
import random, string, django, json
from django.db import connection
from collections import namedtuple
from django.core.files.storage import FileSystemStorage
from django.db.models import Max

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):
    template = loader.get_template('index.html')
    Events = {
                "Events":[{"name":"Amr Diab",
                      "Location":"Cairo festival concert",
                      "img":"cfc.jpg", 'desc':"""Buy tickets for the
                       superstar Amr Diab's cairo festival concert at
                       23 of september 2019"""},
                     {"name":"Mohamed Hamaki",
                      "Location":"Porto sokhna's concert",
                      "img":"hamaki2.jpg", 'desc':"""Buy tickets for the
                       superstar Mohamed Hamaki's porto sokhna concert at
                        25 of october 2019."""},
                     {"name":"Tamer Hosny",
                      "Location":"MUST university concert",
                      "img":"tamer1.jpg", 'desc':"""Buy tickets
                      for the superstar Tamer Hosny's MUST university
                       concert at 26 of augest 2019."""},
                     {"name":"Omar Khairat",
                      "Location":"Cairo opera house concert",
                      "img":"omar khairat.jpg", 'desc':"""Buy tickets
                      for masrah masr next show at MUST university at 28
                      of september 2019."""},
                     {"name":"Angham",
                      "Location":"Cairo opera house concert",
                      "img":"angham.jpg", 'desc':"""Buy tickets for
                       Omar khairat's next opera concert at 29 of
                       september 2019."""}],
                'UserInfo': request.session['UserInfo'],
                'biggest_height': '700',

    }
    print(request.session.get('UserInfo'))
    return HttpResponse(template.render(Events, request))

def activeEvents(request):
    Events = events.objects.all()
    E = [{} for _ in range(len(Events))]
    for i in range(0,len(Events)):
        if request.session['UserInfo'] != '':
            u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
            ue = UserEvent.objects.all().filter(user=u, event=Events[i])
            if ue:
                stat = ue[0].stat
                if len(ue) != 0:
                    if (ue[0].view==True):
                        E[i]['Name']=str(Events[i].name)
                        E[i]['Map']={
                            'locLong':Events[i].locLong,
                            'locLat':Events[i].locLat
                        }
                        E[i]['CreatorID']=Events[i].Creator.id
                        E[i]['id']=Events[i].id
                        E[i]['show']='true'
            else:
                E[i]['Name']=str(Events[i].name)
                E[i]['Map']={
                    'locLong':Events[i].locLong,
                    'locLat':Events[i].locLat
                }
                E[i]['CreatorID']=Events[i].Creator.id
                E[i]['id']=Events[i].id
                E[i]['show']='true'
        else:
            E[i]['Name']=str(Events[i].name)
            E[i]['Map']={
                'locLong':Events[i].locLong,
                'locLat':Events[i].locLat
            }
            E[i]['CreatorID']=Events[i].Creator.id
            E[i]['id']=Events[i].id
            E[i]['show']='true'
    evs = {
        'ev':E,
    }
    return JsonResponse(evs)

def EventHide(request, event):
    if request.method == 'DELETE':
        Event = events.objects.get(id=event)
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        ue = UserEvent.objects.all().filter(user=u, event=Event)
        ue[0].view = False
        ue[0].save()
        return JsonResponse({'Hiding':'Success'})

def EventView(request):
    if request.method == 'GET':
        template = loader.get_template("EventView.html")
        Event = events.objects.get(id=request.GET.get("evID"))
        stat = ''
        if request.session['UserInfo']:
            u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
            ue = UserEvent.objects.all().filter(user=u, event=Event)
            if ue:
                stat = ue[0].stat
        res = {
            'Name':Event.name,
            'description':Event.description,
            'location':Event.location,
            'city':Event.city,
            'id':Event.id,
            #'Map':{
            #    'locLong':Events[i].locLong,
            #    'locLat':Events[i].locLat
            #},
            'booking': str(Event.booking),
            'CreatorName':Event.Creator.displayName,
            'CreatorID':Event.Creator.id,
            'timeFrom':Event.timeFrom,
            'timeTo':Event.timeTo,
            'placeNum':Event.placeNum,
            'attending':stat,
            #EventTypes!!!
        }
        return HttpResponse(template.render(res, request))


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        res = {}
        usres = Users.objects.all().filter(username=username)
        if(usres):
            us=usres[0]
            print(usres)
            if us.verify_password(request.POST.get('password', None)):

                template = loader.get_template("index.html")
                res={
                    'login':'success',
                    'UserInfo':{
                        'username':us.username,
                        'email':us.email,
                        'displayName':us.displayName,
                        #'profilePic':us.profilePic,
                        'id':us.id,
                        #'birthDate':us.birthDate
                    }
                }
                request.session['UserInfo'] = res
                print(request.session['UserInfo'])
                return redirect('/', res)
            else:
                return JsonResponse({'login':'fail'})
            print(res)
            #return JsonResponse(res)
        else:
            template = loader.get_template("Login.html")
            return JsonResponse({'login':'fail'})

    elif request.method == 'GET':
        if(request.session['UserInfo']!=''):
            request.session['UserInfo'] = ''
        template = loader.get_template("Login.html")
        '''u = Users(birthDate="1995-06-21",username = "maged95")
        u.hash_password("Leila")
        u.save()'''
        res = Users.objects.all().filter(username="maged95")
        print(res)
        context = {
            'users':res
        }
        return HttpResponse(template.render(context, request))

def Signup(request):
    if request.method == "POST":
        res1 = Users.objects.filter(username=request.POST.get("username"))
        if res1:
            request.session['Reg_failure'] = {'username':"Server Knows it's Taken"}
            return redirect('/signup/')
            '''VALIDATE PHONENUMBER IS ALL NUMBERS
            VALIDATE DAYS IN MONTH'''
        else:
            u = Users(birthDate=request.POST.get("Year")+"-"+ request.POST.get("Month") +"-" + request.POST.get("Day"),
                      displayName = request.POST.get("displayName"),
                      username = request.POST.get("username"), dayCreated = django.utils.timezone.now(),
                      email = request.POST.get("email"), verified=True)
            u.hash_password(request.POST.get("password"))
            u.save()
            res={
                'login':'success',
                'UserInfo':{
                    'username':u.username,
                    'email':u.email,
                    #'profilePic':us.profilePic,
                    'id':u.id,
                    #'birthDate':us.birthDate
                }
            }
            request.session['UserInfo'] = res
            return redirect("/")
    if request.method == "GET":
        template = loader.get_template("Signup.html")
        context = {
            'months': range(1,13),
            'days': range(1,32),
            'years': range(1940,2000)
        }
        return HttpResponse(template.render(context, request))

def PhoneLogin(request):
    if request.method == "POST":
        print("nol")

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': Users.objects.filter(username=username).exists()
    }
    print(request)
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    return JsonResponse(data)

def GetDaysNum(request):
    month = int(request.POST.get('m', None))
    m1 = [1,3,5,7,8,10,12]
    m2 = [4,6,9,11]
    if month in m1:
        print("yes")

    data = {
        'month': month
    }
    return JsonResponse(data)

def getDaysNum(a):
    m1 = [1,3,5,7,8,10,12]
    return True

def attend(request):
    if request.method == 'POST':
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        e = events.objects.get(id=request.POST.get("evID"))
        ue = UserEvent.objects.all().filter(user=u, event=e)
        if not len(ue)>0:
            newGo = UserEvent(user=u, event=e, stat=2, view=True, time = django.utils.timezone.now())
            newGo.save()
            return JsonResponse({'Attend': 'success'})
        return JsonResponse({'Attend': 'Failure'})

def invite(request):
    if request.method == 'POST':
        u1 = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        u2 = Users.objects.get(id=request.POST.get('uidR'))
        e = events.objects.get(id=request.POST.get('eid'))
        relf = RelStat.objects.all().filter(u1 = u1, u2 = u2).order_by('-time')
        rel = RelStat.objects.all().filter(id__in=relf).distinct('u1','u2')
        if rel and e:
            fRel = rel.filter(stat=5)
            if(fRel):
                inv = invites.objects.all().filter(u1= u1, u2= u2, event=e)
                if(inv):
                    return JsonResponse({'Invite': 'already sent'})
                newIn = invites(u1 = u1, u2 = u2, event= e, seen = False, time = django.utils.timezone.now())
                newIn.save()
                return JsonResponse({'Invite': 'success'})
            else:
                return JsonResponse({'Invite': 'fail'})
        else:
            return JsonResponse({'Invite': 'event or relationship not found'})

def myInvitations(request):
    u2 = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
    ins = invites.objects.all().filter(u2=u2, seen=False)
    if(ins):
        Invs = [{} for _ in range(len(ins))]
        for i in range(0,len(ins)):
            Event = ins[i].event
            Invs[i]['name']=Event.name
            Invs[i]['Description']=Event.description
            Invs[i]['location']=Event.location
            Invs[i]['city']=Event.city
            Invs[i]['id']=Event.id
            Invs[i]['booking']= str(Event.booking)
            Invs[i]['CreatorID']=Event.Creator.id
            Invs[i]['invitationId']=ins[i].id
            Invs[i]['invitor']=ins[i].u1.displayName
            Invs[i]['invitorId']=ins[i].u1.id
        res = {
            'Found':'True',
            'Events':Invs
                #'day':Event.day,
        }
        return JsonResponse(res)
    return JsonResponse({'Found':'False'})

def CreateEvent(request): #EDIT NEEDED
    if request.method == 'POST':
        #type= EventTypes(name="Cinema")
        #type.save()
        t = EventTypes.objects.all().filter(name="Cinema")
        print(request.POST.get('EventName'))
        print(request.session['requestedLocation']['lng'])
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        e = events(name = request.POST.get('EventName'),
                   description = request.POST.get('description'),
                   location= request.POST.get('location'),
                   city= request.POST.get('city'),
                   locLong=request.session['requestedLocation']['lng'],
                   locLat=request.session['requestedLocation']['lat'],
                   booking='True', Creator=u,
                   timeFrom=request.POST.get('Date_From'), timeTo=request.POST.get('Date_To'),
                   ifPlaceNum=True, placeNum=60,
                   dayCreated=django.utils.timezone.now())
        e.save()
        print(request.POST.get('prefs'))
        for p in json.loads(request.POST.get('prefs')):
            et = EventTypes.objects.get(id = str(p))
            e.EventTypes.add(et)
            e.save()
        #e.EventTypes.add(t)
        #e.save()
        print("pass")
        return JsonResponse({'request':'success'})
    elif request.method=='GET':
        if request.session['UserInfo']!='':
            res={
                'lng': request.GET.get('lng'),
                'lat': request.GET.get('lat'),
    	        'mark': request.GET.get('mark'),
            }
            request.session['requestedLocation'] = res
            form = datetimeform()
            template = loader.get_template("EventCreate.html")
            return HttpResponse(template.render({'form': form, 'res':res}, request))
        else:
            return HttpResponse('Please Sign in')

def Find(request):
    Events = {}
    if request.GET.get('city'):
        if request.GET.get('eventType'):
            print("PASS")
            types = EventTypes.objects.all().filter(name=request.GET.get('eventType'))
            if (types):
                Events = events.objects.all().filter(city=request.GET.get('city'), EventTypes = types[0])
            else:
                Events = events.objects.all().filter(city=request.GET.get('city'))
        else:
            Events = events.objects.all().filter(city=request.GET.get('city'))
    elif request.GET.get('eventType'):
        print("pass")
        types = EventTypes.objects.all().filter(name=request.GET.get('eventType'))
        if (types):
            print("Pass")
            Events = events.objects.all().filter(EventTypes = types[0])
    else:
        Events = events.objects.all()
        #u = Users.objects.get(id=Event.CreatorID.id)
    if(Events):
        E = [{} for _ in range(len(Events))]
        for i in range(0,len(Events)):
            E[i]['id']=Events[i].id
            E[i]['Name']=Events[i].name
            E[i]['description']=Events[i].description
            E[i]['location']=Events[i].location
            E[i]['city']=Events[i].city
            E[i]['Map']={
                'locLong':Events[i].locLong,
                'locLat':Events[i].locLat
            }
            E[i]['booking']= str(Events[i].booking)
            E[i]['CreatorID']=Events[i].Creator.id

        res = {
            'Found':'True',
            'Event':E
                #'day':Event.day,

        }
    else:
        res = {
            'Found':'False',
        }
    return JsonResponse(res)

def map(request):
    template = loader.get_template('mainAlt.html')
    if not 'UserInfo' in request.session:
        request.session['UserInfo']=''
    if not 'state' in request.session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        request.session['state']=state
    context = {

    }
    request.META["CSRF_COOKIE_USED"] = True
    return HttpResponse(template.render(context, request))

def displayMyEvents(request):
    us = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])  #request.session['User']["UserInfo"]["username"])
    Events = events.objects.all().filter(Creator=us)
    if(Events):
        print("pass")
        E = [{} for _ in range(len(Events))]
        for i in range(0,len(Events)):
            E[i]['Name']=Events[i].name
            E[i]['description']=Events[i].description
            E[i]['location']=Events[i].location
            E[i]['city']=Events[i].city
            E[i]['id']=Events[i].id
            E[i]['Map']={
                'locLong':Events[i].locLong,
                'locLat':Events[i].locLat
            }
            E[i]['timeFrom']=Events[i].timeFrom,
            E[i]['timeTo']=Events[i].timeTo,
            E[i]['booking']= str(Events[i].booking)
            E[i]['Creator']=Events[i].Creator.id
        print("pass")
        res = {
            'Found':'True',
            'Events':E
                #'day':Event.day,
        }
    else:
        print("fail")
        res = {
            'Found':'false'
                #'day':Event.day,
        }
    template = loader.get_template('myEvents.html')
    return HttpResponse(template.render(res, request))

def displayReservations(request):
    us = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])   #request.session['User']["UserInfo"]["username"])
    Reservations1 = UserEvent.objects.all().filter(user=us).order_by('-time')
    Reservations = UserEvent.objects.all().filter(id__in=Reservations1).distinct('user','event')
    if (Reservations):
        resf = Reservations.filter(stat=2)
        if (resf):
            E = [{} for _ in range(len(resf))]
            for i in range(0,len(resf)):
                Event = resf[i].event
                E[i]['name']=Event.name
                E[i]['Description']=Event.description
                E[i]['location']=Event.location
                E[i]['city']=Event.city
                E[i]['id']=Event.id
                E[i]['booking']= str(Event.booking)
                E[i]['CreatorID']=Event.Creator.id
                E[i]['reservationsId']=resf[i].id
            res = {
                'Found':'True',
                'Events':E
                    #'day':Event.day,
            }
        else:
            res = {
                'Found':'false'
                #'day':Event.day,
            }
    else:
        res = {
            'Found':'false'
                #'day':Event.day,
        }
    template = loader.get_template('myReservations.html')
    return HttpResponse(template.render(res, request))

def CancelEv(request, event):
    if request.method == 'DELETE':
        e = events.objects.get(id=event)
        e.delete()
        print(event)
        return JsonResponse({'request':'success'})

def CancelRes(request, event):
    if request.method == 'DELETE':
        e = events.objects.get(id=event)
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        res1 = UserEvent.objects.all().filter(event=e, user=u).order_by('-time')
        res = UserEvent.objects.all().filter(id__in=res1).distinct('user','event')
        if res[0].stat == 1:
            newRes = UserEvent(event=e, user=u, stat=0, view = True, time=django.utils.timezone.now())
            newRes.save()
            return JsonResponse({'request':'success'})
        else:
            return JsonResponse({'request':'event not reserved'})


def findPref(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM "Eventak_eventtypes" where LOWER(name) LIKE LOWER('%"""+str(request.GET.get('pref'))+"""%')""")
        prefs = namedtuplefetchall(cursor)
        template = loader.get_template('prefSearch.html')
        if(prefs):
            prefsRes = [{} for _ in range(len(prefs))]
            res = {'Found':'True',}
            for i in range(0,len(prefs)):
               prefsRes[i]['id'] = prefs[i].id
               prefsRes[i]['name'] = prefs[i].name
            res['prefs'] = prefsRes
            return HttpResponse(template.render(res, request))
        else:
            return HttpResponse(template.render({'found':'none'}, request))

def findPrefEV(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM "Eventak_eventtypes" where LOWER(name) LIKE LOWER('%"""+str(request.GET.get('pref'))+"""%')""")
        prefs = namedtuplefetchall(cursor)
        template = loader.get_template('prefSearchEV.html')
        if(prefs):
            prefsRes = [{} for _ in range(len(prefs))]
            res = {'Found':'True',}
            for i in range(0,len(prefs)):
               prefsRes[i]['id'] = prefs[i].id
               prefsRes[i]['name'] = prefs[i].name
            res['prefs'] = prefsRes
            return HttpResponse(template.render(res, request))
        else:
            return HttpResponse(template.render({'found':'none'}, request))

def newPref(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM "Eventak_eventtypes" where LOWER(name) LIKE LOWER('%"""+request.POST.get('pref')+"""%')""")
            ets = namedtuplefetchall(cursor)
            if(ets):
                return JsonResponse({'request':'already Exists'})
            else:
                newET = EventTypes(name = request.POST.get('pref'))
                newET.save()
                us = Users.objects.all().filter(id=request.session['UserInfo']['UserInfo']['id'])
                if(us):
                    newP = UserPref(user = us[0], eType = newET, isPref=True, time =django.utils.timezone.now())
                    newP.save()
                    return JsonResponse({'request':'success', 'id':newET.id, 'name':newET.name})

def addPref(request):
    us = Users.objects.get(id=str(request.session['UserInfo']['UserInfo']['id']))
    if(us):
        et = EventTypes.objects.get(id =str(request.POST.get('PrefId')))
        if et:
            up = UserPref.objects.all().filter(user = us, eType=et, isPref=True)
            if(up):
                return JsonResponse({'request':'already done'})
            else:
                newP = UserPref(user = us, eType = et, isPref=True, time =django.utils.timezone.now())
                newP.save()
                return JsonResponse({'request':'success', 'id':et.id, 'name':et.name})
        else:
            return JsonResponse({'request':'Preference not found'})
    else:
        return JsonResponse({'request':'User not Found'})

def UserPage(request):
    u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
    if u:
        up = UserPref.objects.all().filter(user = u, isPref=True)
        if up:
            EvT = [{} for _ in range(len(up))]
            for i in range(0,len(up)):
                EvT[i]['id'] = up[i].eType.id
                EvT[i]['name'] = up[i].eType.name
            res = {
                'load':'success',
                'name':u.displayName,
                'prefs':EvT,
                'prof':u.profilePic,
                'form':UserProfilePic(),
            }
        else:
            res = {
                'load':'success',
                'name':u.displayName,
                'prof':u.profilePic,
                'form':UserProfilePic(),
            }
        template = loader.get_template('UserPage.html')
        return HttpResponse(template.render(res, request))
    else:
        template = loader.get_template('userPage.html')
        return HttpResponse(template.render({'load':'success'}, request))

def updateProfPic(request):
    if request.method == 'POST':
        myfile = request.POST.get('img')
        fs = FileSystemStorage()
        filename = fs.save('mag.jpg', myfile)
        uploaded_file_url = fs.uIrl(filename)
        if form.is_valid():
            handle_uploaded_file(request.FILES['profilePic'])
            return JsonResponse({'request':'success'})
    return HttpResponse(_('Invalid request!'))

def findUserPage(request):
    template = loader.get_template('userSearch.html')
    return HttpResponse(template.render({'load':'Success'}, request))

def findUser(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
           cursor.execute("""SELECT DISTINCT ON(us.id) "displayName",us.id,email,username,"profilePic",stat FROM "Eventak_users" as us LEFT JOIN "Eventak_relstat" as rel ON us.id=rel.u2_id AND rel.u1_id=""" + str(request.session['UserInfo']['UserInfo']['id']) + """ WHERE ((LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%')) OR (LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%'))) GROUP BY us.id,stat,u1_id,u2_id,time ORDER BY us.id,time DESC NULLS LAST""")
           us = namedtuplefetchall(cursor)
           template = loader.get_template('userSearchRes.html')
           if(us):
              usRes = [{} for _ in range(len(us))]
              res = {'Found':'True',}
              for i in range(0,len(us)):
                 usRes[i]['id'] = us[i].id
                 usRes[i]['email'] = us[i].email
                 usRes[i]['username'] = us[i].username
                 usRes[i]['profilePic'] = us[i].profilePic
                 usRes[i]['name'] = us[i].displayName
                 usRes[i]['stat'] = us[i].stat
              res['users'] = usRes
              return HttpResponse(template.render(res, request))
           return HttpResponse(template.render({'user':'none'}, request))

def requestFriendship(request):
    if request.method == 'POST':
        if str(request.session['UserInfo']['UserInfo']['id']) == str(request.POST.get('idR')):
            return JsonResponse({'request':'fail'})
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        ru = Users.objects.get(id = request.POST.get('idR'))
        relation = RelStat.objects.all().filter(u1=ru, u2=u).order_by('-time')
        if(relation):
            if relation[0].stat<=-1 or relation[0].stat>=2:
                return JsonResponse({'request':'fail'})
            else:
                newRel = RelStat(u1=u, u2=ru, stat = 2, time=django.utils.timezone.now())
                newRel.save()
                newRel2 = RelStat(u1=ru, u2=u, stat = 3, time=django.utils.timezone.now())
                newRel2.save()
                return JsonResponse({'request':'success'})
        else:
            newRel = RelStat(u1=u, u2=ru, stat = 2, time=django.utils.timezone.now())
            newRel.save()
            newRel2 = RelStat(u1=ru, u2=u, stat = 3, time=django.utils.timezone.now())
            newRel2.save()
            return JsonResponse({'request':'success'})

def displayArtists(request):
    template = loader.get_template('artist.html')
    u = Users.objects.all().filter(verified=True)
    A = [{} for _ in range(len(u))]
    for i in range(0,len(u)):
        A[i]['name']=u[i].displayName,
        A[i]['picture']=u[i].profilePic,
    res= {
        'Artists':A
    }
    return HttpResponse(template.render(res, request))

def userRequests(request):
    if request.method == 'GET':
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        rel1 = RelStat.objects.all().filter(u1=u).order_by('-time')
        rel = RelStat.objects.all().filter(id__in=rel1).distinct('u1','u2')
        if(rel):
            fRel = rel.filter(stat=3)
            if(fRel):
                usRes = [{} for _ in range(len(fRel))]
                for i in range(0,len(fRel)):
                    ru = Users.objects.get(id=fRel[i].id)
                    usRes[i]['id'] = ru.id
                    usRes[i]['email'] = ru.email
                    usRes[i]['username'] = ru.username
                    #usRes[i]['profilePic'] = ru.profilePic
                    usRes[i]['name'] = ru.displayName
                res = {'requests': usRes}
            else:
                res = {'requests': 'none'}
        else:
            res = {'requests': 'none'}
        template = loader.get_template('userRequests.html')
        return HttpResponse(template.render(res, request))

def acceptFriendRequest(request):
    if request.method == 'POST':
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        ru = Users.objects.get(id = request.POST.get('idR'))
        rel1 = RelStat.objects.all().filter(u1=u, u2=ru).order_by('-time')
        rel = RelStat.objects.all().filter(id__in=rel1).distinct('u1','u2')
        if(rel):
            if rel[0].stat == 3:
                newRel = RelStat(u1=u, u2=ru, stat = 5, time=django.utils.timezone.now())
                newRel.save()
                newRel2 = RelStat(u1=ru, u2=u, stat = 5, time=django.utils.timezone.now())
                newRel2.save()
                return JsonResponse({'request':'success'})
            else:
                return JsonResponse({'request':'No Request Received'})
        else:
            return JsonResponse({'request':'No Request Received'})

def hideFriendRequest(request):
    if request.method == 'POST':
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        ru = Users.objects.get(id = request.POST.get('idR'))
        m = RelStat.objects.latest('time')
        rel1 = RelStat.objects.all().filter(u1=u, u2=ru).order_by('-time')
        rel = RelStat.objects.all().filter(id__in=rel1).distinct('u1','u2')
        if(rel):
            if rel[0].stat == 3:
                newRel = RelStat(u1=u, u2=ru, stat = -1, time=django.utils.timezone.now())
                newRel.save()
                return JsonResponse({'request':'success'})
            else:
                return JsonResponse({'request':'No Request Received'})
        else:
            return JsonResponse({'request':'No Request Received'})

def showFriends(request):
    if request.method == 'GET':
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        rel1 = RelStat.objects.all().filter(u1=u).order_by('-time')
        rel = RelStat.objects.all().filter(id__in=rel1).distinct('u1','u2')
        if(rel):
            fRel = rel.filter(stat=5)
            if(fRel):
                usRes = [{} for _ in range(len(fRel))]
                for i in range(0,len(fRel)):
                    ru = Users.objects.get(id=fRel[i].id)
                    usRes[i]['id'] = str(ru.id)
                    usRes[i]['email'] = ru.email
                    usRes[i]['username'] = ru.username
                    #usRes[i]['profilePic'] = ru.profilePic
                    usRes[i]['name'] = ru.displayName
                res = {'requests': usRes}
            else:
                res = {'requests': 'none'}
        else:
            res = {'requests': 'none'}
        return JsonResponse(res)

def newsfeed(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""select distinct on(u_id,e_id,type) * from ((select '1' as type,u."displayName" as name1,e."locLong",e."logLat",e.name,e.description,e."dayCreated",e.id as e_id,u.id as u_id,e."timeFrom",e."timeTo" from "Eventak_events" AS e JOIN "Eventak_relstat" AS rel on e."Creator_id" = rel.u2_id and rel.u1_id = """ + str(request.session['UserInfo']['UserInfo']['id']) + """ AND rel.stat = 5 JOIN "Eventak_users" AS u ON u.id = rel.u2_id ORDER BY rel.time DESC NULLS LAST, e."dayCreated" DESC NULLS LAST) UNION (SELECT DISTINCT ON(u1_id,u2_id,event_id) '2' as type,u."displayName" as name1,e."locLong",e."logLat",e.name,e.description,e."dayCreated",e.id as e_id,u.id as u_id,e."timeFrom",e."timeTo" FROM "Eventak_events" as e JOIN "Eventak_userevent" as ue ON e.id = ue.event_id JOIN "Eventak_relstat" AS rel ON rel.u2_id = ue.user_id AND rel.stat = 5 AND rel.u1_id= """ + str(request.session['UserInfo']['UserInfo']['id']) + """ JOIN "Eventak_users" AS u ON rel.u2_id = u.id WHERE NOT EXISTS (select '1' as type,u."displayName" as name1,e."locLong",e."logLat",e.name,e.description,e."dayCreated",e.id as e_id,u.id as u_id,e."timeFrom",e."timeTo" from "Eventak_events" AS e JOIN "Eventak_relstat" AS rel on e."Creator_id" = rel.u2_id and rel.u1_id = """ + str(request.session['UserInfo']['UserInfo']['id']) + """ AND rel.stat = 5 JOIN "Eventak_users" AS u ON u.id = rel.u2_id ORDER BY rel.time DESC NULLS LAST, e."dayCreated" DESC NULLS LAST) ORDER BY u1_id, u2_id, event_id, ue.time DESC NULLS LAST, rel.time DESC NULLS LAST) UNION (select '3' as type,et.name as name1,e."locLong",e."logLat",e.name,e.description,e."dayCreated",e.id as e_id,up.user_id as u_id,e."timeFrom",e."timeTo" from "Eventak_events" AS e JOIN "Eventak_events_EventTypes" AS eet ON e.id=eet.events_id JOIN "Eventak_userpref" AS up ON eet.eventtypes_id = up."eType_id" and up.user_id= """ + str(request.session['UserInfo']['UserInfo']['id']) + """ JOIN "Eventak_eventtypes" AS et ON et.id = eet.eventtypes_id WHERE NOT EXISTS (SELECT DISTINCT ON(u1_id,u2_id,event_id) '2' as type,u."displayName" as name1,e."locLong",e."logLat",e.name,e.description,e."dayCreated",e.id as e_id,u.id as u_id,e."timeFrom",e."timeTo" FROM "Eventak_events" as e JOIN "Eventak_userevent" as ue ON e.id = ue.event_id JOIN "Eventak_relstat" AS rel ON rel.u2_id = ue.user_id AND rel.stat = 5 AND rel.u1_id= """ + str(request.session['UserInfo']['UserInfo']['id']) + """ JOIN "Eventak_users" AS u ON rel.u2_id = u.id ORDER BY u1_id, u2_id, event_id, ue.time DESC NULLS LAST, rel.time DESC NULLS LAST) ORDER BY e."dayCreated" DESC NULLS LAST)) as foo ORDER BY type""")
            news = namedtuplefetchall(cursor)
            if(news):
                newsRes = [{} for _ in range(len(news))]
                for i in range(0,len(news)):
                    newsRes[i]['e_id'] = news[i].e_id
                    newsRes[i]['type'] = news[i].type
                    newsRes[i]['u_id'] = news[i].u_id
                    newsRes[i]['name1'] = news[i].name1
                    newsRes[i]['name2'] = news[i].name
                    newsRes[i]['locLong'] = news[i].locLong
                    newsRes[i]['locLat'] = news[i].logLat
                    newsRes[i]['description'] = news[i].description
                    newsRes[i]['dayCreated'] = news[i].dayCreated
                    newsRes[i]['timeFrom'] = news[i].timeFrom
                    newsRes[i]['timeTo'] = news[i].timeTo
                res = {'Found':'True', 'news':newsRes}
                template = loader.get_template('feeds.html')
                return HttpResponse(template.render(res, request))
            return JsonResponse({'Found':'False'})

def notifications(request):
    us =  Users.objects.get(id = request.session['UserInfo']['UserInfo']['id'])
    with connection.cursor() as cursor:
        template = loader.get_template('notifications.html')
        invs = invites.objects.all().filter(u2=us).order_by('u1','u2','event','-time').distinct('u1','u2','event')
        cursor.execute("""select * from (select DISTINCT ON(u1_id,u2_id) * from "Eventak_relstat" where u1_id = """ +str(request.session['UserInfo']['UserInfo']['id'])+ """ GROUP BY id,u1_id,u2_id ORDER BY u1_id,u2_id,time DESC NULLS LAST) as rel where stat = 3""")
        reqs = namedtuplefetchall(cursor)
        if(invs or reqs):
            invRes = [{} for _ in range(len(invs))]
            for i in range(0,len(invs)):
                invRes[i]['senderId'] = invs[i].u1.id
                invRes[i]['senderName'] = invs[i].u1.displayName
                invRes[i]['eventId'] = invs[i].event.id
                invRes[i]['eventName'] = invs[i].event.name
            reqRes = [{} for _ in range(len(reqs))]
            for i in range(0,len(reqs)):
                ru = Users.objects.get(id = reqs[i].u1_id)
                reqRes[i]['senderId'] = reqs[i].id
                reqRes[i]['senderName'] = ru.displayName
            res = {'request':'success', 'invitations':invRes, 'FriendRequests':reqRes}
            return HttpResponse(template.render(res, request))
        return HttpResponse(template.render({'request':'success', 'invitations':'None', 'FriendRequests':'None'}, request))

def ProfImgAdd(request):
    if request.method == 'POST':
        #form = UserProfilePic(data=request.POST, files=request.FILES)
        us =  Users.objects.get(id = request.session['UserInfo']['UserInfo']['id'])
        us.profilePic = request.FILES['img']
        us.save()
        return JsonResponse({"image":"Saved"})

def calcDay(date):
    d = date.split('-')
    day = int(int(d[2])+7)%31
    if(d[1]=='12'):
        if(day < 10):
            return (str(int(d[0])+1)+ '-01-0' + str(day))
    elif (day < 7):
        if (int(d[1])+1 < 10):
            return d[0]+'-0'+str(int(d[1])+1)+'-0'+ str(day)
        else:
            return d[0]+'-'+str(int(d[1])+1)+'-0'+ str(day)
    elif (day < 10):
        return d[0]+'-'+d[1]+'-0'+ str(day)
    return d[0]+'-'+d[1]+'-'+ str(day)
