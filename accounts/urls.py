from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.accueil, name="accueil"),

    path("landing/", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    path("profil/proprietaire/", views.profil_proprietaire, name="profil_proprietaire"),
    path("profil/visiteur/", views.profil_visiteur, name="profil_visiteur"),
    path("changer-mot-de-passe/", views.CustomPasswordChangeView.as_view(), name="changer_mot_de_passe"),
]
