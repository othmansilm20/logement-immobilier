from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from favorites.models import Favori
from .models import Annonce, PhotoAnnonce, SignalementAnnonce
from .forms import AnnonceForm, SignalementAnnonceForm


@login_required
def mes_annonces(request):
    annonces_list = Annonce.objects.filter(
        proprietaire=request.user
    ).order_by("-date_creation")

    total = annonces_list.count()
    publiees = annonces_list.filter(statut="publiee").count()
    en_attente = annonces_list.filter(statut="en_attente").count()
    brouillons = annonces_list.filter(statut="brouillon").count()

    paginator = Paginator(annonces_list, 5)
    page_number = request.GET.get("page")
    annonces = paginator.get_page(page_number)

    return render(request, "owner/mes_annonces.html", {
        "annonces": annonces,
        "total": total,
        "publiees": publiees,
        "en_attente": en_attente,
        "brouillons": brouillons,
    })


@login_required
def creer_annonce(request):
    if request.method == "POST":
        form = AnnonceForm(request.POST, request.FILES)

        if form.is_valid():
            annonce = form.save(commit=False)
            annonce.proprietaire = request.user

            action = request.POST.get("action")

            if action == "soumettre":
                annonce.statut = "en_attente"
                annonce.date_soumission = timezone.now()
                messages.success(request, "Annonce soumise pour validation.")
            else:
                annonce.statut = "brouillon"
                messages.success(request, "Annonce enregistrée en brouillon.")

            annonce.save()

            photos = request.FILES.getlist("photos")

            for photo in photos:
                PhotoAnnonce.objects.create(
                    annonce=annonce,
                    image=photo
                )

            return redirect("properties:mes_annonces")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")

    else:
        form = AnnonceForm()

    return render(request, "owner/creer_annonce.html", {
        "form": form,
        "annonce": None,
    })


@login_required
def modifier_annonce(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, proprietaire=request.user)

    if annonce.statut != "brouillon":
        messages.error(request, "Seules les annonces en brouillon peuvent être modifiées.")
        return redirect("properties:mes_annonces")

    if request.method == "POST":
        form = AnnonceForm(request.POST, request.FILES, instance=annonce)

        if form.is_valid():
            annonce = form.save(commit=False)

            action = request.POST.get("action")

            if action == "soumettre":
                annonce.statut = "en_attente"
                annonce.date_soumission = timezone.now()
                messages.success(request, "Annonce modifiée et soumise pour validation.")
            else:
                annonce.statut = "brouillon"
                messages.success(request, "Annonce modifiée et enregistrée en brouillon.")

            annonce.save()

            photos = request.FILES.getlist("photos")

            for photo in photos:
                PhotoAnnonce.objects.create(
                    annonce=annonce,
                    image=photo
                )

            return redirect("properties:mes_annonces")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")

    else:
        form = AnnonceForm(instance=annonce)

    return render(request, "owner/creer_annonce.html", {
        "form": form,
        "annonce": annonce,
    })


@login_required
def supprimer_annonce(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, proprietaire=request.user)
    annonce.delete()

    messages.success(request, "Annonce supprimée avec succès.")
    return redirect("properties:mes_annonces")


def detail_annonce(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk)
    photos = annonce.photos.all()

    est_favori = False

    if request.user.is_authenticated:
        est_favori = Favori.objects.filter(
            utilisateur=request.user,
            annonce=annonce
        ).exists()

    similaires = Annonce.objects.filter(
        statut="publiee",
        ville=annonce.ville,
        type_bien=annonce.type_bien
    ).exclude(pk=annonce.pk)[:3]

    profil_proprietaire = getattr(annonce.proprietaire, "profile", None)

    return render(request, "visitor/detail_annonce.html", {
        "annonce": annonce,
        "photos": photos,
        "est_favori": est_favori,
        "similaires": similaires,
        "profil_proprietaire": profil_proprietaire,
    })


@login_required
def detail_annonce_owner(request, pk):
    annonce = get_object_or_404(
        Annonce,
        pk=pk,
        proprietaire=request.user
    )

    photos = annonce.photos.all()
    profil_proprietaire = getattr(request.user, "profile", None)

    return render(request, "owner/detail_annonce_owner.html", {
        "annonce": annonce,
        "photos": photos,
        "profil_proprietaire": profil_proprietaire,
    })


@login_required
def signaler_annonce(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, statut="publiee")

    deja_signale = SignalementAnnonce.objects.filter(
        annonce=annonce,
        utilisateur=request.user,
        statut="nouveau"
    ).exists()

    if deja_signale:
        messages.warning(request, "Vous avez déjà signalé cette annonce.")
        return redirect("properties:detail_annonce", pk=annonce.pk)

    if request.method == "POST":
        form = SignalementAnnonceForm(request.POST)

        if form.is_valid():
            signalement = form.save(commit=False)
            signalement.annonce = annonce
            signalement.utilisateur = request.user
            signalement.save()

            messages.success(request, "Signalement envoyé avec succès.")
            return redirect("properties:detail_annonce", pk=annonce.pk)

    else:
        form = SignalementAnnonceForm()

    return render(request, "properties/signaler_annonce.html", {
        "form": form,
        "annonce": annonce
    })