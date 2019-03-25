"""
WSGI config for Eventak2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
from django.http import HttpResponse, JsonResponse
from django.template import loader
from Eventak.models import Users
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

def login(request):
    username = request.POST.get('username')
    usres = Users.objects.all().filter(username=username)
    if(usres):
        us=usres[0]
        print(usres)
        res = ''
        if us.verify_password(request.POST.get('password', None)):
                res={
                    'login':'success',
                    'UserInfo':{
                        'username':us.username,
                        'email':us.email,
                        'profilePic':us.profilePic,
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
