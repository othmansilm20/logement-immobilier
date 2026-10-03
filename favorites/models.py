from django.conf import settings
from django.db import models
from properties.models import Annonce


class Favori(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favoris"
    )

    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.CASCADE,
        related_name="favoris"
    )

    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("utilisateur", "annonce")

    def __str__(self):
        return f"{self.utilisateur.username} - {self.annonce.titre}"