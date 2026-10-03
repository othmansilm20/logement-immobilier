from django.conf import settings
from django.db import models


class Annonce(models.Model):
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("en_attente", "En attente"),
        ("publiee", "Publiée"),
        ("rejetee", "Rejetée"),
        ("archivee", "Archivée"),
    ]

    TYPE_CHOICES = [
        ("appartement", "Appartement"),
        ("maison", "Maison"),
        ("villa", "Villa"),
        ("studio", "Studio"),
    ]

    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="annonces"
    )

    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_bien = models.CharField(max_length=30, choices=TYPE_CHOICES)

    prix = models.DecimalField(max_digits=12, decimal_places=2)
    surface = models.PositiveIntegerField()

    ville = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="brouillon"
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_soumission = models.DateTimeField(null=True, blank=True)
    date_publication = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titre


class SignalementAnnonce(models.Model):
    RAISON_CHOICES = [
        ("fausse", "Fausse annonce"),
        ("prix_suspect", "Prix suspect"),
        ("photos_trompeuses", "Photos trompeuses"),
        ("deja_louee", "Annonce déjà louée"),
        ("contenu_incorrect", "Contenu incorrect"),
        ("autre", "Autre"),
    ]

    STATUT_CHOICES = [
        ("nouveau", "Nouveau"),
        ("traite", "Traité"),
        ("ignore", "Ignoré"),
    ]

    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.CASCADE,
        related_name="signalements"
    )

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="signalements_annonces"
    )

    raison = models.CharField(max_length=50, choices=RAISON_CHOICES)
    message = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="nouveau")
    date_signalement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signalement - {self.annonce.titre} par {self.utilisateur.username}"

class PhotoAnnonce(models.Model):
    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.CASCADE,
        related_name="photos"
    )

    image = models.ImageField(upload_to="annonces/")
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo de {self.annonce.titre}"