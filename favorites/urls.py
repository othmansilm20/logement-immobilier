from django.urls import path
from . import views

app_name = "favorites"

urlpatterns = [
    path("", views.mes_favoris, name="mes_favoris"),
    path("<int:pk>/toggle/", views.toggle_favori, name="toggle_favori"),
]