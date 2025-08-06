from django.db import models
import uuid

class Conducteur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True)
    voiture = models.CharField(max_length=100)
    nombre_places = models.IntegerField()
    code_unique = models.CharField(max_length=10, unique=True, default=uuid.uuid4().hex[:10])

    def __str__(self):
        return f"{self.nom} ({self.telephone})"