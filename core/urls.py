from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('trajets/verifier_code/', views.verifier_code, name='verifier_code'),
    path('trajets/publier/', views.publier_trajet, name='publier_trajet'),
    path('trajets/rechercher/', views.rechercher_trajet, name='rechercher_trajet'),
    path('trajets/<int:trajet_id>/reserver/', views.reserver_place, name='reserver_place'),
    path('suivre-trajet/', views.suivre_trajet, name='suivre_trajet'),
    path('modifier-trajet/<int:trajet_id>/', views.modifier_trajet, name='modifier_trajet'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
]
