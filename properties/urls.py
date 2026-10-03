from django.urls import path
from . import views

app_name = "properties"

urlpatterns = [
    path("annonces/", views.mes_annonces, name="mes_annonces"),
    path("annonces/creer/", views.creer_annonce, name="creer_annonce"),
    path("annonces/<int:pk>/", views.detail_annonce, name="detail_annonce"),
    path("annonces/<int:pk>/modifier/", views.modifier_annonce, name="modifier_annonce"),
    path("annonces/<int:pk>/supprimer/", views.supprimer_annonce, name="supprimer_annonce"),
    path("annonces/<int:pk>/owner/", views.detail_annonce_owner, name="detail_annonce_owner"),
    path("annonces/<int:pk>/signaler/",views.signaler_annonce,name="signaler_annonce"),
]