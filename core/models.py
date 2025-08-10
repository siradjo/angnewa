from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
import re
# ----------- Fonction pour générer un code unique -----------
def generate_code_unique():
    return str(uuid.uuid4()).split('-')[0]
    
# ----------- Manager personnalisé pour Utilisateur -----------
class UtilisateurManager(BaseUserManager):
    def create_user(self, telephone, password=None, **extra_fields):
        if not telephone:
            raise ValueError('Le numéro de téléphone est obligatoire.')
        user = self.model(telephone=telephone, **extra_fields)
        user.set_password(password)
        if not user.code_unique:
            user.code_unique = generate_code_unique()
        user.save()
        return user

    def create_superuser(self, telephone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(telephone, password, **extra_fields)

# ----------- Modèle personnalisé d'utilisateur -----------
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    telephone = models.CharField(max_length=15, unique=True)
    nom = models.CharField(max_length=100, blank=True)
    prenom = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    experience_conduite = models.PositiveIntegerField(default=0)  # années d'expérience
    photo_permis = models.ImageField(upload_to='permis_conduire/', blank=True, null=True)

    code_unique = models.CharField(max_length=10, unique=True, editable=False, default=generate_code_unique)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = []

    def clean(self):
        super().clean()
        tel = self.telephone.replace(" ", "")
        # Ajout +224 si absent
        if not tel.startswith("+"):
            tel = "+224" + tel
        # Vérifie format exact +224 + 9 chiffres
        if not re.match(r'^\+224\d{9}$', tel):
            raise ValidationError({'telephone': "Le numéro doit être au format +224 suivi de 9 chiffres."})
        self.telephone = tel

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.telephone}) - Code: {self.code_unique}"

# ----------- Modèle Trajet -----------
class Trajet(models.Model):
    TYPE_VEHICULE_CHOICES = [
        ('personnel', 'Personnel'),
        ('taxi', 'Taxi'),
        ('minibus', 'Minibus'),
        ('bus', 'Bus'),
    ]

    conducteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    date_heure_depart = models.DateTimeField()
    places_disponibles = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    type_vehicule = models.CharField(max_length=10, choices=TYPE_VEHICULE_CHOICES)
    commentaire = models.TextField(blank=True, null=True)

    # ✅ Photo du véhicule (facultative)
    photo_vehicule = models.ImageField(upload_to='vehicules/', blank=True, null=True)

    # ✅ Total initial de places
    places_totales = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.places_totales = self.places_disponibles
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ville_depart} ➜ {self.ville_arrivee} ({self.date_heure_depart})"

class Reservation(models.Model):
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='reservations')
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    date_reservation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réservation de {self.nom} ({self.telephone}) pour le trajet {self.trajet}"




class StatistiqueTrajet(models.Model):
    chauffeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='statistiques_trajets'
    )
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    date_heure_depart = models.DateTimeField()
    places_totales = models.PositiveIntegerField()
    places_reservees = models.PositiveIntegerField(default=0)
    
    # soit "avec_reservation" soit "sans_reservation"
    STATUT_CHOICES = [
        ('avec_reservation', 'Avec réservation'),
        ('sans_reservation', 'Sans réservation'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    date_archivage = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chauffeur.nom} - {self.ville_depart} → {self.ville_arrivee} ({self.statut})"
