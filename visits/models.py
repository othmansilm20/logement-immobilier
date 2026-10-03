from django.conf import settings
from django.db import models

from properties.models import Annonce


class DemandeVisite(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("acceptee", "Acceptée"),
        ("refusee", "Refusée"),
    ]

    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.CASCADE,
        related_name="demandes_visite"
    )

    visiteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demandes_visite"
    )

    message = models.TextField(blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="en_attente"
    )

    reponse_proprietaire = models.TextField(blank=True, null=True)
    date_reponse = models.DateTimeField(blank=True, null=True)

    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.visiteur.username} pour {self.annonce.titre}"