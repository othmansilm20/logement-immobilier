from django.urls import path
from . import views

app_name = "visits"

urlpatterns = [
    path("annonces/<int:pk>/demander/", views.demander_visite, name="demander_visite"),
    path("proprietaire/demandes/", views.demandes_visite, name="demandes_visite"),
    path("mes-demandes/", views.mes_demandes_visiteur, name="mes_demandes_visiteur"),
    path("<int:pk>/accepter/", views.accepter_demande, name="accepter_demande"),
    path("<int:pk>/refuser/", views.refuser_demande, name="refuser_demande"),
]