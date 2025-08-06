from django.contrib import admin
from .models import Utilisateur, Trajet, Reservation

admin.site.register(Utilisateur)
admin.site.register(Trajet)
admin.site.register(Reservation)
