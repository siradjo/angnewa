import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db.models import F, Q
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.dateformat import format as date_format
from django.http import HttpResponseServerError
from .models import Utilisateur, Trajet, StatistiqueTrajet, Reservation
from .forms import InscriptionChauffeurForm, CodeVerificationForm, TrajetForm, ReservationForm
import logging
logger = logging.getLogger(__name__)


# 🏠 Page d'accueil
def accueil(request):
    ville_depart = request.GET.get('ville_depart', '')
    ville_arrivee = request.GET.get('ville_arrivee', '')

    try:
        # Base queryset
        trajets = Trajet.objects.all()

        # Ajout des filtres dynamiques
        if ville_depart:
            trajets = trajets.filter(ville_depart__icontains=ville_depart)
        if ville_arrivee:
            trajets = trajets.filter(ville_arrivee__icontains=ville_arrivee)

        # Tri obligatoire pour éviter UnorderedObjectListWarning
        trajets = trajets.order_by('-date_heure_depart', '-id')

        # Pagination
        paginator = Paginator(trajets, 8)
        page = request.GET.get('page')

        try:
            trajets_page = paginator.page(page)
        except PageNotAnInteger:
            trajets_page = paginator.page(1)
        except EmptyPage:
            trajets_page = paginator.page(paginator.num_pages)

        return render(request, 'core/accueil.html', {'trajets': trajets_page})

    except Exception as e:
        logger.error(f"[ERREUR] Vue accueil – {str(e)}")
        return HttpResponseServerError("Erreur serveur lors du chargement des trajets.")

# 👤 Inscription chauffeur
def inscription(request):
    if request.method == 'POST':
        form = InscriptionChauffeurForm(request.POST, request.FILES)
        if form.is_valid():
            utilisateur = form.save(commit=False)
            utilisateur.code_unique = uuid.uuid4().hex[:8].upper()
            utilisateur.save()
            return render(request, 'core/confirmation_inscription.html', {'code': utilisateur.code_unique})
    else:
        form = InscriptionChauffeurForm()
    return render(request, 'core/inscription.html', {'form': form})

# 🔐 Vérification code (vue unifiée)
def verifier_code(request):
    # ✅ Si la session est déjà active, on redirige directement
    if request.session.get('conducteur_id'):
        next_page = request.GET.get('next') or request.POST.get('next', '')
        if next_page == 'suivre':
            return redirect('suivre_trajet')
        else:
            return redirect('publier_trajet')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        next_page = request.POST.get('next', '')

        utilisateur = Utilisateur.objects.filter(code_unique=code).first()

        if utilisateur:
            request.session['conducteur_id'] = utilisateur.id  # 🔥 Session activée
            if next_page == 'suivre':
                return redirect('suivre_trajet')
            else:
                return redirect('publier_trajet')
        else:
            return render(request, 'core/verifier_code.html', {
                'erreur': "Code invalide, veuillez réessayer.",
                'next': next_page
            })

    else:
        next_page = request.GET.get('next', '')
        return render(request, 'core/verifier_code.html', {'next': next_page})

# 🚗 Publication de trajet
def publier_trajet(request):
    conducteur_id = request.session.get('conducteur_id')
    
    # Si le conducteur n'est pas encore authentifié via code
    if not conducteur_id:
        messages.warning(request, "Vous devez valider votre code unique avant de publier un trajet.")
        return redirect(f'{reverse("verifier_code")}?next=publier_trajet')

    # Si l'utilisateur envoie un formulaire
    if request.method == 'POST':
        form = TrajetForm(request.POST, request.FILES)
        if form.is_valid():
            trajet = form.save(commit=False)
            trajet.conducteur_id = conducteur_id  # On lie le trajet au conducteur vérifié
            trajet.save()
            messages.success(request, "🚗 Trajet publié avec succès !")
            return redirect('accueil')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = TrajetForm()
    
    return render(request, 'core/publier_trajet.html', {'form': form})

# 📅 Réservation de place
def reserver_place(request, trajet_id):
    trajet = get_object_or_404(Trajet, id=trajet_id)
    if trajet.places_disponibles <= 0:
        messages.error(request, "❌ Ce trajet est déjà complet.")
        return redirect('accueil')

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.trajet = trajet
            reservation.save()
            Trajet.objects.filter(id=trajet.id).update(places_disponibles=F('places_disponibles') - 1)

            if trajet.conducteur.email:
                send_mail(
                    subject="🚗 Nouvelle réservation sur votre trajet",
                    message=(
                        f"Bonjour,\n\nUne nouvelle réservation a été effectuée pour votre trajet :\n"
                        f"{trajet.ville_depart} ➜ {trajet.ville_arrivee} à {trajet.date_heure_depart}.\n"
                        f"Numéro du passager : {reservation.telephone}\n\nMerci."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[trajet.conducteur.email],
                    fail_silently=True,
                )

            date_depart_str = date_format(trajet.date_heure_depart, 'd/m/Y H:i')

            return render(request, 'core/reserver_place.html', {
                'form': ReservationForm(),
                'trajet': trajet,
                'reservation_success': True,
                'date_depart': date_depart_str,
            })

        messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ReservationForm()

    return render(request, 'core/reserver_place.html', {'form': form, 'trajet': trajet})

# 🔍 Recherche de trajets
def rechercher_trajet(request):
    ville_depart = request.GET.get('ville_depart')
    ville_arrivee = request.GET.get('ville_arrivee')

    try:
        trajets = Trajet.objects.all()
        print("Trajets récupérés")

        if ville_depart:
            trajets = trajets.filter(ville_depart__icontains=ville_depart)
            print(f"Filtré par ville_depart: {ville_depart}")
        if ville_arrivee:
            trajets = trajets.filter(ville_arrivee__icontains=ville_arrivee)
            print(f"Filtré par ville_arrivee: {ville_arrivee}")

        trajets = trajets.order_by('-date_heure_depart', '-id')
        print("Tri effectué")

        paginator = Paginator(trajets, 8)
        page = request.GET.get('page')
        print(f"Page demandée : {page}")

        try:
            trajets_page = paginator.page(page)
        except PageNotAnInteger:
            trajets_page = paginator.page(1)
            print("Page non entière, retour à la première page")
        except EmptyPage:
            trajets_page = paginator.page(paginator.num_pages)
            print("Page vide, retour à la dernière page")

        return render(request, 'core/rechercher_trajet.html', {'trajets': trajets_page})

    except Exception as e:
        import traceback
        traceback.print_exc()  # Affiche l'erreur complète dans la console
        logger.error(f"Erreur dans la vue rechercher_trajet : {str(e)}")
        return HttpResponseServerError("Erreur serveur lors de la recherche.")

# 📍 Suivi de trajet
def suivre_trajet(request):
    conducteur_id = request.session.get('conducteur_id')

    # Si non connecté par code unique, redirection vers vérification
    if not conducteur_id:
        return redirect(f'{reverse("verifier_code")}?next=suivre_trajet')

    # Vérifie que le conducteur existe
    try:
        conducteur = Utilisateur.objects.get(id=conducteur_id)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        request.session.flush()
        return redirect(f'{reverse("verifier_code")}?next=suivre_trajet')

    maintenant = timezone.now()

    # Suppression d’un trajet (POST)
    if request.method == "POST":
        trajet_id = request.POST.get("trajet_id")
        trajet = get_object_or_404(Trajet, id=trajet_id, conducteur=conducteur)

        if trajet.reservations.exists():
            messages.error(request, "❌ Impossible de supprimer un trajet avec des réservations.")
        else:
            trajet.delete()
            messages.success(request, "✅ Trajet supprimé avec succès.")

        return redirect('suivre_trajet')

    # Trajets actifs (à venir)
    trajets_actifs = Trajet.objects.filter(conducteur=conducteur, date_heure_depart__gte=maintenant)

    # Trajets archivés
    trajets_archives = StatistiqueTrajet.objects.filter(chauffeur=conducteur)

    # Réservations globales
    reservations_totales = Reservation.objects.filter(trajet__conducteur=conducteur).count()
    trajets_avec_reservations = Trajet.objects.filter(
        conducteur=conducteur,
        reservations__isnull=False
    ).distinct().count()

    # Construction des détails par trajet
    trajets_avec_details = []
    for trajet in trajets_actifs.order_by('-date_heure_depart'):
        reservations = trajet.reservations.all().order_by('date_reservation')
        places_reservees = reservations.count()
        places_restantes = trajet.places_disponibles
        modifiable = (places_reservees == 0)

        trajets_avec_details.append({
            'trajet': trajet,
            'reservations': reservations,
            'nombre_reservations': places_reservees,
            'places_restantes': places_restantes,
            'places_totales': places_restantes + places_reservees,
            'modifiable': modifiable,
        })

    # Données envoyées au template
    context = {
        'conducteur': conducteur,
        'trajets_actifs_count': trajets_actifs.count(),
        'trajets_archives_count': trajets_archives.count(),
        'reservations_totales': reservations_totales,
        'trajets_avec_reservations': trajets_avec_reservations,
        'trajets_avec_details': trajets_avec_details,
    }

    return render(request, 'core/suivre_trajet.html', context)

# ✏️ Modifier un trajet existant
def modifier_trajet(request, trajet_id):
    trajet = get_object_or_404(Trajet, id=trajet_id)

    if request.method == 'POST':
        form = TrajetForm(request.POST, instance=trajet)
        if form.is_valid():
            form.save()
            return redirect('suivre_trajet')
    else:
        form = TrajetForm(instance=trajet)

    return render(request, 'core/modifier_trajet.html', {'form': form, 'trajet': trajet})

# 🚪 Déconnexion
def deconnexion(request):
    request.session.flush()
    return redirect('accueil')
