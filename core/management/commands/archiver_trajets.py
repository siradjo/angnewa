from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Trajet, StatistiqueTrajet
from datetime import timedelta

class Command(BaseCommand):
    help = "Archive tous les trajets terminés (date de départ dépassée), et supprime ceux archivés depuis plus de 8 mois."

    def handle(self, *args, **options):
        maintenant = timezone.now()

        # 1. ARCHIVER les trajets dont la date de départ est déjà passée
        trajets_termines = Trajet.objects.filter(date_heure_depart__lt=maintenant)
        total_archives = 0

        for trajet in trajets_termines:
            places_reservees = max(0, trajet.places_totales - trajet.places_disponibles)
            statut = 'avec_reservation' if places_reservees > 0 else 'sans_reservation'

            # On enregistre les infos dans StatistiqueTrajet
            StatistiqueTrajet.objects.create(
                chauffeur=trajet.conducteur,
                ville_depart=trajet.ville_depart,
                ville_arrivee=trajet.ville_arrivee,
                date_heure_depart=trajet.date_heure_depart,
                places_totales=trajet.places_totales,
                places_reservees=places_reservees,
                statut=statut
            )

            trajet.delete()
            total_archives += 1

        self.stdout.write(self.style.SUCCESS(f"{total_archives} trajets archivés."))

        # 2. SUPPRIMER les statistiques trop anciennes (plus de 8 mois)
        limite_archive = maintenant - timedelta(days=240)
        archives_supprimees = StatistiqueTrajet.objects.filter(date_heure_depart__lt=limite_archive)
        total_supprimees = archives_supprimees.count()
        archives_supprimees.delete()

        self.stdout.write(self.style.SUCCESS(f"{total_supprimees} archives supprimées (plus de 8 mois)."))
