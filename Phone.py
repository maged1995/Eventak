"""
WSGI config for Eventak2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from Eventak.models import Users, RelStat
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
                        'email':'',
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
           cursor.execute("""SELECT DISTINCT ON(f2id_id,us.id) "displayName",us.id,email,username,"profilePic",stat FROM "Eventak_users" as us LEFT JOIN "Eventak_relstat" as rel ON us.id=rel.f2id_id AND rel.f1id_id=""" + str(request.GET.get('myID')) + """ AND stat >= -1 WHERE ((LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%')) OR (LOWER("displayName") LIKE LOWER('%"""+request.GET.get('nameR')+"""%'))) GROUP BY us.id,stat,f1id_id,f2id_id,time ORDER BY us.id, f2id_id, time DESC NULLS LAST""")
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

def requestFriendship(request):
    if request.method == 'GET':
        u = Users.objects.get(id=str(request.GET.get('myID')))
        ru = Users.objects.get(id= request.GET.get('idR'))
        relation = RelStat.object.all().filter(f1id=ru, f2id=u)
        if(relation):
            if relation[0].stat<=-1 or r==relation[0].stat==3:
                return JsonResponse({'request':'success'})
            else:
                newRel = RelStat(f1id=ru, f2id=u, stat = 2)
                newRel.save()
                return JsonResponse({'request':'success'})
        else:
            newRel = RelStat(f1id=ru, f2id=u, stat = 2)
            newRel.save()
            return JsonResponse({'request':'success'})

def userRequests(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""select * from (select DISTINCT ON(f1id_id,f2id_id) * from "Eventak_relstat" where f1id_id = """ +str(request.GET.get('myID'))+ """ GROUP BY id,f1id_id,f2id_id ORDER BY f1id_id,f2id_id,time DESC NULLS LAST) as rel where stat = 3""")
            rel = views.namedtuplefetchall(cursor)
            if(rel):
                usRes = [{} for _ in range(len(rel))]
                for i in range(0,len(rel)):
                    u = Users.objects.get(id=rel[i].f2id_id)
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
        rel = RelStat.objects.all().filter(f1id=u, f2id=ru).order_by('f1id','f2id','-time').distinct('f1id','f2id')
        if(rel):
            if(rel[0].stat == 3 or rel[0].stat == -1):
                newRel = RelStat(f1id=u, f2id=ru, stat = 5, time=django.utils.timezone.now())
                newRel.save()
                newRel2 = RelStat(f1id=ru, f2id=u, stat = 5, time=django.utils.timezone.now())
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
        rel = RelStat.objects.all().filter(f1id=u, f2id=ru).order_by('f1id','f2id','-time').distinct('f1id','f2id')
        if(rel):
            if(rel[0].stat == 3):
                newRel = RelStat(f1id=u, f2id=ru, stat = -1, time=django.utils.timezone.now())
                newRel.save()
                return JsonResponse({'request':'success'})
            else:
                return JsonResponse({'request':'failure'})
        else:
            return JsonResponse({'request':'No Request Receive'})
