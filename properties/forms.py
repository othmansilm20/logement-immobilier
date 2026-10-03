from django import forms
from .models import Annonce
from .models import SignalementAnnonce


class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = [
            "titre",
            "description",
            "type_bien",
            "prix",
            "surface",
            "ville",
            "adresse",
            "latitude",
            "longitude",
        ]

        widgets = {
            "titre": forms.TextInput(attrs={
                "placeholder": "Ex: Bel appartement 3 pièces en centre-ville"
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Décrivez votre bien...",
                "rows": 4
            }),
            "type_bien": forms.Select(),
            "prix": forms.NumberInput(attrs={
                "placeholder": "Ex: 250000"
            }),
            "surface": forms.NumberInput(attrs={
                "placeholder": "Ex: 75"
            }),
            "ville": forms.TextInput(attrs={
                "placeholder": "Ex: Casablanca"
            }),
            "adresse": forms.TextInput(attrs={
                "placeholder": "Ex: 15 rue de la République"
            }),
            "latitude": forms.NumberInput(attrs={
                "step": "any",
                "placeholder": "Ex: 33.5731"
            }),
            "longitude": forms.NumberInput(attrs={
                "step": "any",
                "placeholder": "Ex: -7.5898"
            }),
        }


class SignalementAnnonceForm(forms.ModelForm):
    class Meta:
        model = SignalementAnnonce
        fields = ["raison", "message"]

        widgets = {
            "raison": forms.Select(attrs={
                "class": "form-control"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Expliquez brièvement le problème..."
            }),
        }

        labels = {
            "raison": "Raison du signalement",
            "message": "Message complémentaire",
        }        