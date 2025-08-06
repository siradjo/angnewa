from django import forms
from .models import Utilisateur, Trajet, Reservation



class InscriptionChauffeurForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'telephone', 'email', 'experience_conduite', 'photo_permis']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'experience_conduite': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'photo_permis': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CodeVerificationForm(forms.Form):
    code_unique = forms.CharField(label="Code unique", max_length=10)



class TrajetForm(forms.ModelForm):
    class Meta:
        model = Trajet
        fields = [
            'ville_depart', 'ville_arrivee', 'date_heure_depart',
            'places_disponibles', 'prix', 'type_vehicule', 'photo_vehicule', 'commentaire',
        ]
        widgets = {
            'date_heure_depart': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }




class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['nom', 'telephone', 'email']
