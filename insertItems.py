from django.http import HttpResponse, JsonResponse
from django.template import loader
from Eventak.models import events, Users, UserEvent, EventTypes, RelStat
from django.shortcuts import redirect
import django


def init(request):
    """type= EventTypes(name="Cinema")
    type.save()

    u = Users(birthDate="1995-06-21",username = "maged95", displayName = "Maged A. Saad", dayCreated=django.utils.timezone.now(), verified=True)
    u.hash_password("Leila")
    u.save()

    t = EventTypes.objects.all().filter(name="Cinema")
    u = Users.objects.get(id=1)

    e = events(name = 'Avengers: Endgame',
               description = 'Movie',
               location= 'City Stars',
               city= 'Cairo',
               locLong='30.044235', locLat='31.235540', booking='True', Creator=u,
               timeFrom='2019-06-21 08:30', timeTo='2019-06-21 21:30', ifPlaceNum=True, placeNum=60, dayCreated=django.utils.timezone.now())
    e.save()
    e.EventTypes.set(t)
    
    e = events.objects.get(id=1)
    u = Users.objects.get(id=1)
    R = UserEvent(event= e, user=u, stat=1, view=True, time=django.utils.timezone.now())
    R.save()
    
    u2 = Users(birthDate="1995-06-21",username = "Moh", displayName = "Mohamed Hamed", email="mohamed@gmail.com", dayCreated=django.utils.timezone.now(),verified=True)
    u2.hash_password("Leila")
    u2.save()

    R.save()"""
    u = Users.objects.get(id=1)
    u2 = Users.objects.get(id=2)

    re = RelStat(u1 = u, u2 = u2, stat=3, time=django.utils.timezone.now())
    re.save()

    return redirect("/")
