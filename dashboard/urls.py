from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("owner/", views.owner_dashboard, name="owner_dashboard"),
    path("visitor/", views.visitor_dashboard, name="visitor_dashboard"),

    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/profil/", views.profil_admin, name="profil_admin"),
   path("admin-panel/utilisateurs/", views.admin_utilisateurs, name="admin_utilisateurs"),

    path(
    "admin-panel/utilisateurs/<int:pk>/",
    views.admin_detail_utilisateur,
    name="admin_detail_utilisateur"),
 
    path(
    "admin-panel/utilisateurs/<int:pk>/modifier/",
    views.admin_modifier_utilisateur,
    name="admin_modifier_utilisateur"),

    path(
    "admin-panel/utilisateurs/<int:pk>/activer-desactiver/",
    views.admin_toggle_utilisateur,
    name="admin_toggle_utilisateur"),

    path("admin-panel/utilisateurs/<int:pk>/supprimer/",views.admin_supprimer_utilisateur,name="admin_supprimer_utilisateur"),
    path("admin-panel/annonces-a-valider/", views.admin_valider, name="admin_valider"),
    path("admin-panel/annonces/", views.admin_annonces, name="admin_annonces"),

   path("admin-panel/annonces/<int:pk>/approuver/", views.admin_approuver, name="admin_approuver"),
   path("admin-panel/annonces/<int:pk>/rejeter/", views.admin_rejeter, name="admin_rejeter"),
   path("admin-panel/annonces/<int:pk>/supprimer/", views.admin_supprimer_annonce, name="admin_supprimer_annonce"),
   path("admin-panel/annonces/<int:pk>/detail/", views.admin_detail_annonce, name="admin_detail_annonce"),
   path("admin-panel/annonces/<int:pk>/modifier/",views.admin_modifier_annonce,name="admin_modifier_annonce"),

   path(
    "admin-panel/signalements/",
    views.admin_signalements,
    name="admin_signalements"
),

path(
    "admin-panel/signalements/<int:pk>/traiter/",
    views.admin_marquer_signalement_traite,
    name="admin_marquer_signalement_traite"
),

path(
    "admin-panel/signalements/<int:pk>/ignorer/",
    views.admin_ignorer_signalement,
    name="admin_ignorer_signalement"
),

path(
    "admin-panel/signalements/<int:pk>/archiver-annonce/",
    views.admin_archiver_annonce_signalement,
    name="admin_archiver_annonce_signalement"
),        
]
