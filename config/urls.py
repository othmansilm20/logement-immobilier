from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve as serve_static
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

admin.site.site_header = "LogementImmo"
admin.site.site_title = "LogementImmo"
admin.site.index_title = "Administration de la plateforme"


urlpatterns = [
    path("django-admin/", admin.site.urls),

    path("", include("accounts.urls")),
    path("accounts/", include("accounts.urls", namespace="accounts_prefixed")),
    path("dashboard/", include("dashboard.urls")),
    path("properties/", include("properties.urls")),
    path("visits/", include("visits.urls")),
    path("favorites/", include("favorites.urls")),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("changer-mot-de-passe/",auth_views.PasswordChangeView.as_view(template_name="accounts/changer_mot_de_passe.html",success_url="/"),name="changer_mot_de_passe"),
    
]

# Petit projet de demo : Django sert aussi les fichiers media en production
# (WhiteNoise ne gere que les fichiers statiques, pas les uploads utilisateur).
# `django.conf.urls.static.static()` refuse de fonctionner hors DEBUG, on
# ajoute donc la route manuellement avec la meme vue.
urlpatterns += [
    re_path(
        r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
        serve_static,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
