from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from properties.models import Annonce
from .models import DemandeVisite
from django.utils import timezone


@login_required
def demander_visite(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, statut="publiee")

    demande_existante = DemandeVisite.objects.filter(
        annonce=annonce,
        visiteur=request.user,
        statut="en_attente"
    ).exists()

    if demande_existante:
        messages.warning(request, "Vous avez déjà une demande en attente pour cette annonce.")
        return redirect("properties:detail_annonce", pk=pk)

    if request.method == "POST":
        message = request.POST.get("message", "")

        DemandeVisite.objects.create(
            annonce=annonce,
            visiteur=request.user,
            message=message
        )

        messages.success(request, "Votre demande de visite a été envoyée.")
        return redirect("properties:detail_annonce", pk=pk)

    return render(request, "visitor/demander_visite.html", {
        "annonce": annonce
    })


@login_required
def demandes_visite(request):
    demandes = DemandeVisite.objects.filter(
        annonce__proprietaire=request.user
    ).select_related(
        "annonce",
        "visiteur",
        "visiteur__profile"
    ).order_by("-date_demande")

    return render(request, "owner/demandes_visite.html", {
        "demandes": demandes
    })


@login_required
def accepter_demande(request, pk):
    demande = get_object_or_404(
        DemandeVisite,
        pk=pk,
        annonce__proprietaire=request.user
    )

    if request.method == "POST":
        reponse = request.POST.get("reponse_proprietaire", "").strip()

        demande.statut = "acceptee"
        demande.reponse_proprietaire = reponse or "Votre demande de visite a été acceptée."
        demande.date_reponse = timezone.now()
        demande.save()

        messages.success(request, "La demande de visite a été acceptée.")
        return redirect("visits:demandes_visite")

    return redirect("visits:demandes_visite")


@login_required
def refuser_demande(request, pk):
    demande = get_object_or_404(
        DemandeVisite,
        pk=pk,
        annonce__proprietaire=request.user
    )

    if request.method == "POST":
        reponse = request.POST.get("reponse_proprietaire", "").strip()

        demande.statut = "refusee"
        demande.reponse_proprietaire = reponse or "Votre demande de visite a été refusée."
        demande.date_reponse = timezone.now()
        demande.save()

        messages.warning(request, "La demande de visite a été refusée.")
        return redirect("visits:demandes_visite")

    return redirect("visits:demandes_visite")

@login_required
def mes_demandes_visiteur(request):
    demandes = DemandeVisite.objects.filter(
        visiteur=request.user
    ).select_related("annonce").order_by("-date_demande")

    return render(request, "visitor/mes_demandes.html", {
        "demandes": demandes
    })