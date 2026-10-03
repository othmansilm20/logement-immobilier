from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from favorites.models import Favori
from visits.models import DemandeVisite


def landing(request):
    form = request.GET.get("form", "login")
    role = request.GET.get("role", "")

    return render(request, "landing.html", {
        "show_register": form == "register",
        "role": role,
    })


def login_view(request):
    role = request.GET.get("role", "")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            profile, created = Profile.objects.get_or_create(user=user)

            if role == "admin":
                if not user.is_staff and not user.is_superuser:
                    messages.error(request, "Vous n'avez pas l'autorisation d'accéder à l'espace admin.")
                    return render(request, "landing.html", {"role": role, "show_register": False})

                login(request, user)
                return redirect("dashboard:admin_dashboard")

            elif role == "proprietaire":
                if profile.role != "proprietaire":
                    messages.error(request, "Ce compte n'est pas un compte propriétaire.")
                    return render(request, "landing.html", {"role": role, "show_register": False})

                login(request, user)
                return redirect("dashboard:owner_dashboard")

            elif role == "visiteur":
                if profile.role != "visiteur":
                    messages.error(request, "Ce compte n'est pas un compte visiteur.")
                    return render(request, "landing.html", {"role": role, "show_register": False})

                login(request, user)
                return redirect("dashboard:visitor_dashboard")

            messages.error(request, "Rôle invalide.")
            return render(request, "landing.html", {"role": role, "show_register": False})

        messages.error(request, "Email ou mot de passe incorrect.")

    return render(request, "landing.html", {"role": role, "show_register": False})


def logout_view(request):
    logout(request)
    return redirect("accounts:accueil")


def register_view(request):
    logout(request)
    role = request.GET.get("role", "visiteur")

    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        prenom = request.POST.get("prenom", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        email = (request.POST.get("email") or request.POST.get("username") or "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role", "visiteur").strip()

        User = get_user_model()

        if role not in ["visiteur", "proprietaire"]:
            role = "visiteur"

        if not email:
            messages.error(request, "Veuillez renseigner une adresse email valide.")
            return render(request, "landing.html", {"show_register": True, "role": role})

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "landing.html", {"show_register": True, "role": role})

        if User.objects.filter(username=email).exists():
            messages.error(request, "Cet email est déjà utilisé comme nom d'utilisateur.")
            return render(request, "landing.html", {"show_register": True, "role": role})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, "landing.html", {"show_register": True, "role": role})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=prenom,
            last_name=nom
        )

        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.telephone = telephone
        profile.save()

        messages.success(request, "Compte créé avec succès. Vous pouvez maintenant vous connecter.")
        return redirect(f"{reverse_lazy('accounts:login')}?role={role}")

    return render(request, "landing.html", {"show_register": True, "role": role})


@login_required
def profil_proprietaire(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect("accounts:profil_proprietaire")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "owner/profil.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


@login_required
def profil_visiteur(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    demandes = DemandeVisite.objects.filter(visiteur=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect("accounts:profil_visiteur")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "visitor/profil.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "favoris_count": Favori.objects.filter(utilisateur=request.user).count(),
        "demandes_count": demandes.count(),
        "demandes_acceptees": demandes.filter(statut="acceptee").count(),
    })


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/changer_mot_de_passe.html"

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return reverse_lazy("dashboard:profil_admin")

        if hasattr(user, "profile") and user.profile.role == "proprietaire":
            return reverse_lazy("accounts:profil_proprietaire")

        return reverse_lazy("accounts:profil_visiteur")


def accueil(request):
    return render(request, "accueil.html")
