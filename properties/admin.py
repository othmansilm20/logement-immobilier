from django.contrib import admin
from .models import Annonce, PhotoAnnonce, SignalementAnnonce


class PhotoAnnonceInline(admin.TabularInline):
    model = PhotoAnnonce
    extra = 1


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "proprietaire",
        "ville",
        "prix",
        "surface",
        "type_bien",
        "statut",
        "date_creation",
    )

    list_filter = (
        "statut",
        "type_bien",
        "ville",
        "date_creation",
    )

    search_fields = (
        "titre",
        "description",
        "ville",
        "adresse",
        "proprietaire__username",
        "proprietaire__email",
    )

    inlines = [PhotoAnnonceInline]


@admin.register(PhotoAnnonce)
class PhotoAnnonceAdmin(admin.ModelAdmin):
    list_display = (
        "annonce",
        "image",
        "date_ajout",
    )


@admin.register(SignalementAnnonce)
class SignalementAnnonceAdmin(admin.ModelAdmin):
    list_display = (
        "annonce",
        "utilisateur",
        "raison",
        "statut",
        "date_signalement",
    )

    list_filter = (
        "statut",
        "raison",
        "date_signalement",
    )

    search_fields = (
        "annonce__titre",
        "utilisateur__username",
        "utilisateur__email",
        "message",
    )