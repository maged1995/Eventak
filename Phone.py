"""
WSGI config for Eventak2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from Eventak.models import Users, RelStat, events, UserEvent, invites
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.db import connection
from . import views
import string, django

def login(request):
    username = request.GET.get('username')
    usres = Users.objects.all().filter(username=username)
    if(usres):
        us=usres[0]
        print(usres)
        res = ''
        if us.verify_password(request.GET.get('password', None)):
                res={
                    'login':'success',
                    'UserInfo':{
                        'username':us.username,
                        'email':us.email,
                        'id':us.id
                        ###'profilePic':us.profilePic,
                        #'birthDate':us.birthDate
                    }
                }
        else:
                res = {
                        'login':'fail'
                }
        print(res)
    else:
        res = {
                'login':'fail'
        }
    return JsonResponse(res)
    #return HttpResponse(template.render(res, request))

def Signup(request):
    if request.method == "GET":
        res1 = Users.objects.filter(username=request.GET.get("username"))
        if res1:
            return JsonResponse({'request':'username already Taken'})
        else:
            u = Users(birthDate= request.GET.get("Year")+"-"+ request.GET.get("Month") +"-" + request.GET.get("Day"), displayName = request.GET.get("displayName"),
                      username = request.GET.get("username"), dayCreated = django.utils.timezone.now(),
                      email = request.GET.get("email"), verified=True)
            u.hash_password(request.GET.get("password"))
            u.save()
            return JsonResponse({'request':'success'})


def attend(request):
    if request.method == 'GET':
        u = Users.objects.get(id=request.GET.get("myID"))
        e = events.objects.get(id=request.GET.get("evID"))
        ue = UserEvent.objects.all().filter(user=u, event=e)
        if not len(ue)>0:
            newGo = UserEvent(user=u, event=e, stat=2, view=True, time = django.utils.timezone.now())
            newGo.save()
            return JsonResponse({'Attend': 'success'})
        return JsonResponse({'Attend': 'already on Attend'})

@csrf_exempt
def PhoneLogin(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer = UsersSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

def Find(request):
    if request.method == 'GET':
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
                E[i]['id']=str(Events[i].id)
                E[i]['Name']=str(Events[i].name)
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
                'Events':E
                    #'day':Event.day,

            }
        else:
            res = {
                'Found':'False',
            }
        return JsonResponse(res)

def findUser(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
           cursor.execute("""SELECT DISTINCT ON(u2_id,us.id) "displayName",us.id,email,username,"profilePic",stat FROM "Eventak_users" as us LEFT JOIN "Eventak_relstat" as rel ON us.id=rel.u2_id AND rel.u1_id=""" + str(request.GET.get('myID')) + """ AND stat >= -1 WHERE ((LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%')) OR (LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%'))) GROUP BY us.id,stat,u1_id,u2_id,time ORDER BY us.id, u2_id, time DESC NULLS LAST""")
           us = views.namedtuplefetchall(cursor)
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
              return JsonResponse({'result':res})
           return JsonResponse({'user':'none'})

def findUserByUsername(request):
    if request.method == 'GET':
        u = Users.objects.get(id = str(request.GET.get('myID')))
        ru = Users.objects.all().filter(username = request.GET.get('nameR'))
        if ru:
            res = {'Found':'True', 'id':ru[0].id, 'email':ru[0].email, 'username':ru[0].username, 'name':ru[0].displayName,}
            rel = RelStat.objects.all().filter(u1=u, u2=ru[0]).order_by('-time')
            if rel:
                res['stat'] = rel[0].stat
            else:
                res['stat'] = 0
            return JsonResponse({'result':res})
        else:
            return JsonResponse({'result':'not found'})

def requestFriendship(request):
    if request.method == 'GET' and request.GET.get('myID')!=request.GET.get('idR'):
        u = Users.objects.get(id=request.GET.get('myID'))
        ru = Users.objects.get(id= request.GET.get('idR'))
        relation = RelStat.objects.all().filter(u1=ru, u2=u).order_by('-time')
        if(relation):
            if relation[0].stat<=-1 or relation[0].stat>1:
                return JsonResponse({'request':'already done'})
            else:
                newRel = RelStat(u1=u, u2=ru, stat = 2, time = django.utils.timezone.now())
                newRel.save()
                newRel2 = RelStat(u1=ru, u2=u, stat = 3, time=django.utils.timezone.now())
                newRel2.save()
                return JsonResponse({'request':'success'})
        else:
            newRel = RelStat(u1=u, u2=ru, stat = 2, time = django.utils.timezone.now())
            newRel.save()
            newRel2 = RelStat(u1=ru, u2=u, stat = 3, time=django.utils.timezone.now())
            newRel2.save()
            return JsonResponse({'request':'success'})

def userRequests(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""select * from (select DISTINCT ON(u1_id,u2_id) * from "Eventak_relstat" where u1_id = """ +str(request.GET.get('myID'))+ """ GROUP BY id,u1_id,u2_id ORDER BY u1_id,u2_id,time DESC NULLS LAST) as rel where stat = 3""")
            rel = views.namedtuplefetchall(cursor)
            if(rel):
                usRes = [{} for _ in range(len(rel))]
                for i in range(0,len(rel)):
                    u = Users.objects.get(id=rel[i].u2_id)
                    usRes[i]['id'] = u.id
                    usRes[i]['email'] = u.email
                    usRes[i]['username'] = u.username
                    #usRes[i]['profilePic'] = u.profilePic
                    usRes[i]['name'] = u.displayName
                res = {'requests': usRes}
            else:
                res = {'requests': 'none'}
            return JsonResponse(res)

def acceptFriendRequest(request):
    if request.method == 'GET':
        u = Users.objects.get(id=str(request.GET.get('myID')))
        ru = Users.objects.get(id = request.GET.get('idR'))
        rel = RelStat.objects.all().filter(u1=u, u2=ru).order_by('u1','u2','-time').distinct('u1','u2')
        if(rel):
            if(rel[0].stat == 3 or rel[0].stat == -1):
                newRel = RelStat(u1=u, u2=ru, stat = 5, time=django.utils.timezone.now())
                newRel.save()
                newRel2 = RelStat(u1=ru, u2=u, stat = 5, time=django.utils.timezone.now())
                newRel2.save()
                return JsonResponse({'request':'success'})
            else:
                return JsonResponse({'request':'failure'})
        else:
            return JsonResponse({'request':'No Request Receive'})

def hideFriendRequest(request):
    if request.method == 'GET':
        u = Users.objects.get(id=str(request.GET.get('myID')))
        ru = Users.objects.get(id = request.GET.get('idR'))
        rel = RelStat.objects.all().filter(u1=u, u2=ru).order_by('u1','u2','-time').distinct('u1','u2')
        if(rel):
            if(rel[0].stat == 3):
                newRel = RelStat(u1=u, u2=ru, stat = -1, time=django.utils.timezone.now())
                newRel.save()
                return JsonResponse({'request':'success'})
            else:
                return JsonResponse({'request':'failure'})
        else:
            return JsonResponse({'request':'No Request Receive'})

def showFriends(request):
    if request.method == 'GET':
        u = Users.objects.get(id=str(request.GET.get('myID')))
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

def invite(request):
    if request.method == 'GET':
        u1 = Users.objects.get(id=request.GET.get('myID'))
        u2 = Users.objects.get(id=request.GET.get('uidR'))
        e = events.objects.get(id=request.GET.get('eid'))
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
    u2 = Users.objects.get(id=request.GET.get('myID'))
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
        res = {
            'Found':'True',
            'Events':Invs
                #'day':Event.day,
        }
        return JsonResponse(res)
    return JsonResponse({'Found':'False'})

def displayReservations(request):
    us = Users.objects.get(id=request.GET.get('myID'))   #request.session['User']["UserInfo"]["username"])
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
    return JsonResponse(res)
