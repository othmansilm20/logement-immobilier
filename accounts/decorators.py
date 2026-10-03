from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def proprietaire_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, "profile") and request.user.profile.role == "proprietaire":
            return view_func(request, *args, **kwargs)

        messages.error(request, "Accès refusé : espace propriétaire uniquement.")
        return redirect("accounts:landing")

    return wrapper


def visiteur_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, "profile") and request.user.profile.role == "visiteur":
            return view_func(request, *args, **kwargs)

        messages.error(request, "Accès refusé : espace visiteur uniquement.")
        return redirect("accounts:landing")

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Accès refusé : espace administrateur uniquement.")
        return redirect("accounts:landing")

    return wrapper