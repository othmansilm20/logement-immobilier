from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from properties.models import Annonce
from .models import Favori


@login_required
def toggle_favori(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, statut="publiee")

    favori, created = Favori.objects.get_or_create(
        utilisateur=request.user,
        annonce=annonce
    )

    if not created:
        favori.delete()
        messages.info(request, "Annonce retirée des favoris.")
    else:
        messages.success(request, "Annonce ajoutée aux favoris.")

    return redirect("properties:detail_annonce", pk=pk)


@login_required
def mes_favoris(request):
    favoris = Favori.objects.filter(
        utilisateur=request.user
    ).select_related("annonce").order_by("-date_ajout")

    return render(request, "visitor/favoris.html", {
        "favoris": favoris
    })