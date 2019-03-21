from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from Eventak.models import Users
import random, string

def index(request):
    template = loader.get_template('index.html')
    if not 'login' in request.session:
        request.session['login']=''
    if not 'state' in request.session:
        state = ''.join(random.choice(string.ascii_uppercase +
                                string.digits) for x in range(32))
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
                "login": request.session["login"],

    }
    return HttpResponse(template.render(Events, request))

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
                        'profilePic':us.profilePic,
                        #'birthDate':us.birthDate
                    }
                }
                request.session['login'] = res
                return redirect('/', res)
            else:
                res = {
                    'login':'fail'
                }
                template = loader.get_template("Login.html")
                return redirect("/login/")
            print(res)
            #return JsonResponse(res)
        else:
            template = loader.get_template("Login.html")
            return redirect("/login/")

    elif request.method == 'GET':
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
    if request.method == "GET":
        template = loader.get_template("Signup.html")
        context = {

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
    print(data)
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    return JsonResponse(data)
