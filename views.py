from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from Eventak.models import events, Users, Reservations, EventTypes, UserEvent, RelStat
from .forms import datetimeform
import random, string, django
from django.db import connection
from collections import namedtuple

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):
    template = loader.get_template('index.html')
    if not 'UserInfo' in request.session:
        request.session['UserInfo']=''
    if not 'state' in request.session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        request.session['state']=state
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
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        ue = UserEvent.objects.all().filter(user=u, event=Events[i])
        if len(ue) != 0:
            if (ue[0].view=='True'):
                E[i]['Name']=str(Events[i].name)
                E[i]['Map']={
                    'locLong':Events[i].locLong,
                    'locLat':Events[i].locLat
                }
                E[i]['CreatorID']=Events[i].Creator.id
                E[i]['id']=Events[i].id
                E[i]['show']='true'
            else:
                E[i]['show']='false'
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
        u = Users.objects.get(id=request.session['UserInfo']['UserInfo']['id'])
        ue = UserEvent.objects.all().filter(user=u, event=Event)
        stat = ''
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
            u = Users(birthDate="1995-06-21",
                      username = request.POST.get("username"),
                      email = request.POST.get("email"), verified=True)
            u.hash_password("Leila")
            u.save()
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
            newGo = UserEvent(user=u, event=e, stat=1, view=True)
            newGo.save()
            return JsonResponse({'Attend': 'success'})
        return JsonResponse({'Attend': 'Failure'})

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
        #e.EventTypes.add(t)
        #e.save()
        print("pass")
        return redirect("/")
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
            return HttpResponse(template.render({'form': form}, request))
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
            E[i]['Name']=str(Events[i].name),
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
    us = Users.objects.get(id=1)  #request.session['User']["UserInfo"]["username"])
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
    Reservations = UserEvent.objects.all().filter(user=us, stat=1)
    if (Reservations):
        E = [{} for _ in range(len(Reservations))]
        for i in range(0,len(Reservations)):
            Event = Reservations[i].event
            E[i]['name']=Event.name
            E[i]['Description']=Event.description
            E[i]['location']=Event.location
            E[i]['city']=Event.city
            E[i]['id']=Event.id
            E[i]['booking']= str(Event.booking)
            E[i]['CreatorID']=Event.Creator.id
            E[i]['reservationsId']=Reservations[i].id
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
        res = UserEvent.objects.all().filter(event=e, user=u)
        res[0].stat = 0
        res[0].save()
        print(event)
        return JsonResponse({'request':str(res[0].event.id)})

def findUserPage(request):
    template = loader.get_template('userSearch.html')
    return HttpResponse(template.render({'load':'Success'}, request))

def findUser(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
           cursor.execute("""SELECT "displayName",us.id,email,username,"profilePic",stat FROM "Eventak_users" as us LEFT JOIN "Eventak_relstat" as rel ON us.id=rel.f1id_id AND rel.f2id_id=""" + str(request.session['UserInfo']['UserInfo']['id']) + """ AND stat >= 0 AND ((LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%')) OR (LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%'))) GROUP BY us.id,stat,f1id_id,f2id_id""")
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
        relation = RelStat.objects.all().filter(f1id=ru, f2id=u)
        if(relation):
            if relation[0].stat<=-1 or relation[0].stat<=2:
                return JsonResponse({'request':'fail'})
            else:
                newRel = RelStat(f1id=u, f2id=ru, stat = 2, time=django.utils.timezone.now())
                newRel.save()
                newRel2 = RelStat(f1id=ru, f2id=u, stat = 3, time=django.utils.timezone.now())
                newRel2.save()
                return JsonResponse({'request':'success'})
        else:
            newRel = RelStat(f1id=u, f2id=ru, stat = 2, time=django.utils.timezone.now())
            newRel.save()
            newRel2 = RelStat(f1id=ru, f2id=u, stat = 3, time=django.utils.timezone.now())
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
        ru = Users.objects.get(id = request.POST.get('idR'))
        relation = RelStat.objects.all().filter(f1id=u, f2id=ru, stat=3)
        if(relation):
            usRes = [{} for _ in range(len(relation))]
            for i in range(0,len(relation)):
                usRes[i]['id'] = us[i].id
                usRes[i]['email'] = us[i].email
                usRes[i]['username'] = us[i].username
                usRes[i]['profilePic'] = us[i].profilePic
                usRes[i]['name'] = us[i].displayName
            res = {'requests': usRes}
        else:
            res = {'requests': 'none'}
        template = loader.get_template('userRequests.html')
        return HttpResponse(template.render(res, request))
