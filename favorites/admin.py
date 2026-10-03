from django.contrib import admin
from .models import Favori


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = (
        "utilisateur",
        "annonce",
        "date_ajout",
    )

    list_filter = (
        "date_ajout",
    )

    search_fields = (
        "utilisateur__username",
        "annonce__titre",
    )
