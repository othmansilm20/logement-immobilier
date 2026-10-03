from django.contrib import messages
from accounts.decorators import proprietaire_required, visiteur_required, admin_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q

from properties.models import Annonce, PhotoAnnonce, SignalementAnnonce
from django.contrib.auth.forms import UserChangeForm
from visits.models import DemandeVisite
from accounts.forms import UserUpdateForm, ProfileUpdateForm
from accounts.models import Profile

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@proprietaire_required
def owner_dashboard(request):
    annonces = Annonce.objects.filter(
        proprietaire=request.user
    ).order_by("-date_creation")

    total = annonces.count()
    publiees = annonces.filter(statut="publiee").count()
    en_attente = annonces.filter(statut="en_attente").count()
    brouillons = annonces.filter(statut="brouillon").count()

    dernieres_annonces = annonces[:5]

    # Notifications : demandes de visite en attente
    nb_notifications = DemandeVisite.objects.filter(
    annonce__proprietaire=request.user
    ).count()

    # Demandes récentes pour l'affichage en bas du dashboard
    demandes_recentes = DemandeVisite.objects.filter(
        annonce__proprietaire=request.user
    ).select_related(
        "annonce",
        "visiteur"
    ).order_by("-date_demande")[:2]

    context = {
        "total": total,
        "publiees": publiees,
        "en_attente": en_attente,
        "brouillons": brouillons,
        "dernieres_annonces": dernieres_annonces,
        "nb_notifications": nb_notifications,
        "demandes_recentes": demandes_recentes,
    }

    return render(request, "owner/dashboard.html", context)


@login_required
def visitor_dashboard(request):
    annonces = Annonce.objects.filter(statut="publiee").order_by("-date_creation")

    q = request.GET.get("q", "").strip()
    ville = request.GET.get("ville", "").strip()
    type_bien = request.GET.get("type_bien", "").strip()
    prix_max = request.GET.get("prix_max", "").strip()
    surface_min = request.GET.get("surface_min", "").strip()

    if q:
        annonces = annonces.filter(
            Q(titre__icontains=q) |
            Q(description__icontains=q) |
            Q(ville__icontains=q) |
            Q(adresse__icontains=q)
        )

    if ville:
        annonces = annonces.filter(ville__iexact=ville)

    if type_bien:
        annonces = annonces.filter(type_bien=type_bien)

    if prix_max:
        try:
            annonces = annonces.filter(prix__lte=prix_max)
        except ValueError:
            pass

    if surface_min:
        try:
            annonces = annonces.filter(surface__gte=surface_min)
        except ValueError:
            pass

    villes = Annonce.objects.filter(
        statut="publiee"
    ).exclude(
        ville__isnull=True
    ).exclude(
        ville=""
    ).values_list(
        "ville", flat=True
    ).distinct().order_by("ville")

    context = {
        "annonces": annonces,
        "villes": villes,
    }

    return render(request, "visitor/dashboard.html", context)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    User = get_user_model()

    total_utilisateurs = User.objects.count()
    total_annonces = Annonce.objects.count()
    nb_attente = Annonce.objects.filter(statut="en_attente").count()
    nb_publiees = Annonce.objects.filter(statut="publiee").count()

    annonces_attente = (
        Annonce.objects
        .filter(statut="en_attente")
        .select_related("proprietaire")
        .prefetch_related("photos")
        .order_by("-date_soumission", "-date_creation")[:5]
    )

    context = {
        "total_utilisateurs": total_utilisateurs,
        "total_annonces": total_annonces,
        "nb_attente": nb_attente,
        "nb_publiees": nb_publiees,
        "annonces_attente": annonces_attente,
    }

    return render(request, "admin_panel/dashboard.html", context)


@login_required
@user_passes_test(is_admin)
def profil_admin(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if profile.role != "admin":
        profile.role = "admin"
        profile.save(update_fields=["role"])

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Votre profil a ete mis a jour avec succes.")
            return redirect("dashboard:profil_admin")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "admin_panel/profil_admin.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "total_utilisateurs": get_user_model().objects.count(),
        "total_annonces": Annonce.objects.count(),
        "signalements_nouveaux": SignalementAnnonce.objects.filter(statut="nouveau").count(),
    })


@login_required
@user_passes_test(is_admin)
def admin_utilisateurs(request):
    User = get_user_model()

    users = User.objects.select_related("profile").all().order_by("-date_joined")

    q = request.GET.get("q", "")
    role = request.GET.get("role", "")
    statut = request.GET.get("statut", "")

    # Recherche par nom, email, prénom, nom
    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    # Filtre par rôle métier
    if role == "admin":
        users = users.filter(is_superuser=True)
    elif role == "proprietaire":
        users = users.filter(profile__role="proprietaire")
    elif role == "visiteur":
        users = users.filter(profile__role="visiteur")

    # Filtre par statut
    if statut == "actif":
        users = users.filter(is_active=True)
    elif statut == "inactif":
        users = users.filter(is_active=False)

    context = {
        "users": users,
        "q": q,
        "role": role,
        "statut": statut,
    }

    return render(request, "admin_panel/utilisateurs.html", context)

@login_required
@user_passes_test(is_admin)
def admin_detail_utilisateur(request, pk):
    User = get_user_model()
    utilisateur = get_object_or_404(User, pk=pk)

    annonces = Annonce.objects.filter(proprietaire=utilisateur).order_by("-date_creation")

    context = {
        "utilisateur": utilisateur,
        "annonces": annonces,
    }

    return render(request, "admin_panel/detail_utilisateur.html", context)


@login_required
@user_passes_test(is_admin)
def admin_toggle_utilisateur(request, pk):
    User = get_user_model()
    utilisateur = get_object_or_404(User, pk=pk)

    if utilisateur == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect("dashboard:admin_utilisateurs")

    if request.method == "POST":
        utilisateur.is_active = not utilisateur.is_active
        utilisateur.save()

        if utilisateur.is_active:
            messages.success(request, "Le compte utilisateur a été activé avec succès.")
        else:
            messages.warning(request, "Le compte utilisateur a été désactivé avec succès.")

    return redirect("dashboard:admin_utilisateurs")

@login_required
@user_passes_test(is_admin)
def admin_modifier_utilisateur(request, pk):
    User = get_user_model()
    utilisateur = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=utilisateur)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        role = request.POST.get("role")
        role_metier = request.POST.get("role_metier", profile.role)
        is_active = request.POST.get("is_active") == "on"
        nouveau_mot_de_passe = request.POST.get("nouveau_mot_de_passe", "").strip()
        confirmer_mot_de_passe = request.POST.get("confirmer_mot_de_passe", "").strip()

        if nouveau_mot_de_passe or confirmer_mot_de_passe:
            if nouveau_mot_de_passe != confirmer_mot_de_passe:
                messages.error(request, "Les deux mots de passe ne correspondent pas.")
                return render(request, "admin_panel/modifier_utilisateur.html", {
                    "utilisateur": utilisateur,
                    "profile": profile,
                })

            try:
                validate_password(nouveau_mot_de_passe, user=utilisateur)
            except ValidationError as erreur:
                for message in erreur.messages:
                    messages.error(request, message)
                return render(request, "admin_panel/modifier_utilisateur.html", {
                    "utilisateur": utilisateur,
                    "profile": profile,
                })

            utilisateur.set_password(nouveau_mot_de_passe)

        utilisateur.username = username
        utilisateur.email = email
        utilisateur.first_name = first_name
        utilisateur.last_name = last_name
        utilisateur.is_active = is_active

        if role == "admin":
            utilisateur.is_staff = True
            utilisateur.is_superuser = True
        elif role == "staff":
            utilisateur.is_staff = True
            utilisateur.is_superuser = False
        else:
            utilisateur.is_staff = False
            utilisateur.is_superuser = False

        utilisateur.save()

        if role_metier in dict(Profile.ROLE_CHOICES):
            profile.role = role_metier

        if request.POST.get("delete_photo") == "on":
            profile.photo.delete(save=False)
            profile.photo = None

        nouvelle_photo = request.FILES.get("photo")
        if nouvelle_photo:
            profile.photo = nouvelle_photo

        profile.save()

        if nouveau_mot_de_passe:
            messages.success(request, "L'utilisateur a été modifié et son mot de passe réinitialisé avec succès.")
        else:
            messages.success(request, "L'utilisateur a été modifié avec succès.")

        return redirect("dashboard:admin_utilisateurs")

    return render(request, "admin_panel/modifier_utilisateur.html", {
        "utilisateur": utilisateur,
        "profile": profile,
        "role_choices": Profile.ROLE_CHOICES,
    })

@login_required
@user_passes_test(is_admin)
def admin_supprimer_utilisateur(request, pk):
    User = get_user_model()
    utilisateur = get_object_or_404(User, pk=pk)

    # Empêcher l'admin de supprimer son propre compte
    if utilisateur == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect("dashboard:admin_utilisateurs")

    # Supprimer seulement avec POST
    if request.method == "POST":
        username = utilisateur.username
        utilisateur.delete()
        messages.success(request, f"L'utilisateur {username} a été supprimé avec succès.")
        return redirect("dashboard:admin_utilisateurs")

    return redirect("dashboard:admin_utilisateurs")


@login_required
@user_passes_test(is_admin)
def admin_valider(request):
    annonces = (
        Annonce.objects
        .filter(statut="en_attente")
        .select_related("proprietaire")
        .prefetch_related("photos")
    )

    ville = request.GET.get("ville", "")
    type_bien = request.GET.get("type_bien", "")
    tri = request.GET.get("tri", "")
    q = request.GET.get("q", "")

    if ville:
        annonces = annonces.filter(ville__icontains=ville)

    if type_bien:
        annonces = annonces.filter(type_bien=type_bien)

    if q:
        annonces = annonces.filter(
            Q(titre__icontains=q) |
            Q(description__icontains=q) |
            Q(ville__icontains=q) |
            Q(proprietaire__username__icontains=q)
        )

    if tri == "ancienne":
        annonces = annonces.order_by("date_soumission")
    else:
        annonces = annonces.order_by("-date_soumission")

    villes = (
        Annonce.objects
        .filter(statut="en_attente")
        .values_list("ville", flat=True)
        .distinct()
        .order_by("ville")
    )

    context = {
        "annonces": annonces,
        "villes": villes,
        "ville": ville,
        "type_bien": type_bien,
        "tri": tri,
        "q": q,
        "nb_attente": annonces.count(),
    }

    return render(request, "admin_panel/annonces_a_valider.html", context)


@login_required
@user_passes_test(is_admin)
def admin_annonces(request):
    annonces = (
        Annonce.objects
        .select_related("proprietaire")
        .prefetch_related("photos")
        .all()
    )

    q = request.GET.get("q", "")
    statut = request.GET.get("statut", "")
    ville = request.GET.get("ville", "")
    type_bien = request.GET.get("type_bien", "")
    tri = request.GET.get("tri", "")

    if q:
        annonces = annonces.filter(
            Q(titre__icontains=q) |
            Q(description__icontains=q) |
            Q(ville__icontains=q) |
            Q(proprietaire__username__icontains=q) |
            Q(proprietaire__email__icontains=q)
        )

    if statut:
        annonces = annonces.filter(statut=statut)

    if ville:
        annonces = annonces.filter(ville__icontains=ville)

    if type_bien:
        annonces = annonces.filter(type_bien=type_bien)

    if tri == "ancienne":
        annonces = annonces.order_by("date_creation")
    else:
        annonces = annonces.order_by("-date_creation")

    villes = (
        Annonce.objects
        .values_list("ville", flat=True)
        .distinct()
        .order_by("ville")
    )

    context = {
        "annonces": annonces,
        "total_annonces": Annonce.objects.count(),
        "villes": villes,
    }

    return render(request, "admin_panel/toutes_annonces.html", context)


@login_required
@user_passes_test(is_admin)
def admin_approuver(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk)

    annonce.statut = "publiee"
    annonce.date_publication = timezone.now()
    annonce.save()

    messages.success(request, "L'annonce a été approuvée avec succès.")
    return redirect("dashboard:admin_dashboard")


@login_required
@user_passes_test(is_admin)
def admin_rejeter(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk)

    annonce.statut = "rejetee"
    annonce.save()

    messages.warning(request, "L'annonce a été rejetée.")
    return redirect("dashboard:admin_dashboard")


@login_required
@user_passes_test(is_admin)
def admin_supprimer_annonce(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk)
    annonce.delete()

    messages.success(request, "L'annonce a été supprimée avec succès.")
    return redirect("dashboard:admin_annonces")

@login_required
@user_passes_test(is_admin)
def admin_detail_annonce(request, pk):
    annonce = get_object_or_404(
        Annonce.objects.select_related("proprietaire").prefetch_related("photos"),
        pk=pk
    )

    photos = annonce.photos.all()
    profil_proprietaire = getattr(annonce.proprietaire, "profile", None)

    return render(request, "admin_panel/detail_annonce_admin.html", {
        "annonce": annonce,
        "photos": photos,
        "profil_proprietaire": profil_proprietaire,
    })

@login_required
@user_passes_test(is_admin)
def admin_modifier_annonce(request, pk):
    annonce = get_object_or_404(
        Annonce.objects.prefetch_related("photos"),
        pk=pk
    )

    if request.method == "POST":
        annonce.titre = request.POST.get("titre")
        annonce.description = request.POST.get("description")
        annonce.type_bien = request.POST.get("type_bien")
        annonce.prix = request.POST.get("prix")
        annonce.surface = request.POST.get("surface")
        annonce.ville = request.POST.get("ville")
        annonce.adresse = request.POST.get("adresse")
        annonce.statut = request.POST.get("statut")

        annonce.save()

        for photo in annonce.photos.all():
            if request.POST.get(f"delete_photo_{photo.pk}") == "on":
                photo.delete()
                continue

            nouvelle_image = request.FILES.get(f"photo_{photo.pk}")
            if nouvelle_image:
                photo.image = nouvelle_image
                photo.save(update_fields=["image"])

        for image in request.FILES.getlist("photos"):
            PhotoAnnonce.objects.create(annonce=annonce, image=image)

        messages.success(request, "L'annonce a été modifiée avec succès.")
        return redirect("dashboard:admin_annonces")

    return render(request, "admin_panel/modifier_annonce_admin.html", {
        "annonce": annonce,
        "photos": annonce.photos.all(),
    }) 


@login_required
@user_passes_test(is_admin)
def admin_signalements(request):
    signalements = (
        SignalementAnnonce.objects
        .select_related("annonce", "utilisateur", "annonce__proprietaire")
        .all()
        .order_by("-date_signalement")
    )

    statut = request.GET.get("statut", "")
    q = request.GET.get("q", "")

    if statut:
        signalements = signalements.filter(statut=statut)

    if q:
        signalements = signalements.filter(
            Q(annonce__titre__icontains=q) |
            Q(utilisateur__username__icontains=q) |
            Q(annonce__proprietaire__username__icontains=q)
        )

    context = {
        "signalements": signalements,
        "statut": statut,
        "q": q,
        "total_signalements": signalements.count(),
    }

    return render(request, "admin_panel/signalements.html", context)


@login_required
@user_passes_test(is_admin)
def admin_marquer_signalement_traite(request, pk):
    signalement = get_object_or_404(SignalementAnnonce, pk=pk)

    if request.method == "POST":
        signalement.statut = "traite"
        signalement.save()
        messages.success(request, "Le signalement a été marqué comme traité.")

    return redirect("dashboard:admin_signalements")


@login_required
@user_passes_test(is_admin)
def admin_ignorer_signalement(request, pk):
    signalement = get_object_or_404(SignalementAnnonce, pk=pk)

    if request.method == "POST":
        signalement.statut = "ignore"
        signalement.save()
        messages.info(request, "Le signalement a été ignoré.")

    return redirect("dashboard:admin_signalements")


@login_required
@user_passes_test(is_admin)
def admin_archiver_annonce_signalement(request, pk):
    signalement = get_object_or_404(SignalementAnnonce, pk=pk)

    if request.method == "POST":
        annonce = signalement.annonce
        annonce.statut = "archivee"
        annonce.save()

        signalement.statut = "traite"
        signalement.save()

        messages.success(request, "L'annonce a été archivée et le signalement traité.")

    return redirect("dashboard:admin_signalements")  
