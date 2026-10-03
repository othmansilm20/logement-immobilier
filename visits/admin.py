from django.contrib import admin
from .models import DemandeVisite


@admin.register(DemandeVisite)
class DemandeVisiteAdmin(admin.ModelAdmin):
    list_display = (
        "annonce",
        "visiteur",
        "statut",
        "date_demande",
        "date_reponse",
    )

    list_filter = (
        "statut",
        "date_demande",
    )

    search_fields = (
        "annonce__titre",
        "visiteur__username",
        "visiteur__email",
    )
