from django.shortcuts import render, redirect
from .models import Conducteur
import uuid

def accueil(request):
    return render(request, 'accueil.html')

def inscription(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email', '')
        voiture = request.POST.get('voiture')
        nombre_places = request.POST.get('nombre_places')
        code_unique = uuid.uuid4().hex[:10]

        conducteur = Conducteur.objects.create(
            nom=nom,
            telephone=telephone,
            email=email,
            voiture=voiture,
            nombre_places=nombre_places,
            code_unique=code_unique
        )
        return render(request, 'code_unique.html', {'code': conducteur.code_unique})

    return render(request, 'inscription.html')