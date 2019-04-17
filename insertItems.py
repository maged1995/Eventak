from django.http import HttpResponse, JsonResponse
from django.template import loader
from Eventak.models import events, Users, reservations, EventTypes
from django.shortcuts import redirect

def init(request):
    type= EventTypes(name="Cinema")
    type.save()

    u = Users(birthDate="1995-06-21",username = "maged95")
    u.hash_password("Leila")
    u.save()

    t = EventTypes.objects.all().filter(name="Cinema")
    u = Users.objects.get(id=1)

    e = events(name = 'Avengers: Endgame',
               description = 'Movie',
               location= 'City Stars',
               city= 'Cairo',
               locLong='30.044235', locLat='31.235540', booking='True', Creator=u,
               timeFrom='2019-06-21 08:30', timeTo='2019-06-21 21:30', ifPlaceNum=True, placeNum=60)
    e.save()
    e.EventTypes.set(t)

    e = events.objects.get(id=1)

    R = reservations(event= e, user=u, quantity=1, status=1)
    R.save()
    return redirect("/")
