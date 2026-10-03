from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from favorites.models import Favori
from properties.models import Annonce, PhotoAnnonce, SignalementAnnonce
from visits.models import DemandeVisite

User = get_user_model()

VILLE_COORDS = {
    "Casablanca": (33.5731, -7.5898),
    "Rabat": (34.0209, -6.8416),
    "Marrakech": (31.6295, -7.9811),
}

ANNONCES = [
    dict(proprio="karim@example.com", titre="Appartement lumineux centre-ville",
         description="Bel appartement 3 pieces proche des commodites.", type_bien="appartement",
         prix=650000, surface=85, ville="Casablanca", adresse="12 Rue Allal Ben Abdellah",
         statut="publiee", photo="annonces/deco-appartement-parisien.jpg"),
    dict(proprio="karim@example.com", titre="Studio meuble pour etudiant",
         description="Studio ideal pour etudiant, proche universite.", type_bien="studio",
         prix=250000, surface=28, ville="Casablanca", adresse="5 Avenue Hassan II",
         statut="publiee", photo="annonces/Renovation-apprtement-Les-Sables-dOlonne-11042022-1604-1280x720.webp"),
    dict(proprio="sara@example.com", titre="Villa avec jardin",
         description="Villa spacieuse avec jardin et garage.", type_bien="villa",
         prix=1800000, surface=220, ville="Rabat", adresse="Quartier Agdal",
         statut="publiee", photo="annonces/TARROU-Combas.webp"),
    dict(proprio="sara@example.com", titre="Maison familiale a renover",
         description="Maison a fort potentiel, travaux a prevoir.", type_bien="maison",
         prix=900000, surface=140, ville="Rabat", adresse="Quartier Hay Riad",
         statut="en_attente", photo="annonces/images.jpg"),
    dict(proprio="nadia@example.com", titre="Riad traditionnel renove",
         description="Riad au coeur de la medina, entierement renove.", type_bien="maison",
         prix=2200000, surface=180, ville="Marrakech", adresse="Derb El Hammam",
         statut="publiee", photo="annonces/20013675828_e4edf95180_b.jpg"),
    dict(proprio="nadia@example.com", titre="Appartement vue palmeraie",
         description="Appartement moderne avec vue degagee sur la palmeraie.", type_bien="appartement",
         prix=980000, surface=95, ville="Marrakech", adresse="Route de Fes",
         statut="publiee", photo="annonces/premium_photo-1661883964999-c1bcb57a7357.avif"),
    dict(proprio="karim@example.com", titre="Local a usage commercial reconverti",
         description="Ancien local, annonce non conforme, a titre d'exemple rejete.", type_bien="studio",
         prix=150000, surface=20, ville="Casablanca", adresse="Ain Sebaa",
         statut="rejetee", photo="annonces/house_background.jpg"),
    dict(proprio="sara@example.com", titre="Appartement deja loue",
         description="Cette annonce a ete archivee suite a un signalement.", type_bien="appartement",
         prix=500000, surface=70, ville="Rabat", adresse="Hassan",
         statut="archivee", photo="annonces/deco-appartement-parisien.jpg"),
]


class Command(BaseCommand):
    help = "Cree un jeu de donnees de demonstration (idempotent : sans doublon si relance)."

    def handle(self, *args, **options):
        admin = self._get_or_create_user("admin@example.com", "admin@example.com", "Admin1234", "admin")
        if not admin.is_superuser:
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()

        self._get_or_create_user("karim@example.com", "karim@example.com", "demo1234", "proprietaire", "Casablanca")
        self._get_or_create_user("sara@example.com", "sara@example.com", "demo1234", "proprietaire", "Rabat")
        self._get_or_create_user("nadia@example.com", "nadia@example.com", "demo1234", "proprietaire", "Marrakech")
        visiteur1 = self._get_or_create_user("youssef@example.com", "youssef@example.com", "demo1234", "visiteur", "Casablanca")
        visiteur2 = self._get_or_create_user("imane@example.com", "imane@example.com", "demo1234", "visiteur", "Marrakech")
        visiteur3 = self._get_or_create_user("amine@example.com", "amine@example.com", "demo1234", "visiteur", "Fes")

        annonces = []
        for data in ANNONCES:
            proprio = User.objects.get(username=data["proprio"])
            lat, lng = VILLE_COORDS.get(data["ville"], (31.7917, -7.0926))

            annonce, created = Annonce.objects.get_or_create(
                titre=data["titre"],
                defaults=dict(
                    proprietaire=proprio,
                    description=data["description"],
                    type_bien=data["type_bien"],
                    prix=data["prix"],
                    surface=data["surface"],
                    ville=data["ville"],
                    adresse=data["adresse"],
                    statut=data["statut"],
                    latitude=lat,
                    longitude=lng,
                ),
            )
            if created:
                if annonce.statut in ("publiee", "en_attente", "rejetee", "archivee"):
                    annonce.date_soumission = timezone.now()
                if annonce.statut == "publiee":
                    annonce.date_publication = timezone.now()
                annonce.save()
                PhotoAnnonce.objects.create(annonce=annonce, image=data["photo"])
            annonces.append(annonce)

        by_titre = {a.titre: a for a in annonces}

        Favori.objects.get_or_create(utilisateur=visiteur1, annonce=by_titre["Appartement lumineux centre-ville"])
        Favori.objects.get_or_create(utilisateur=visiteur2, annonce=by_titre["Villa avec jardin"])
        Favori.objects.get_or_create(utilisateur=visiteur3, annonce=by_titre["Riad traditionnel renove"])

        DemandeVisite.objects.get_or_create(
            annonce=by_titre["Appartement lumineux centre-ville"],
            visiteur=visiteur1,
            defaults={"message": "Bonjour, serait-il possible de visiter ce week-end ?", "statut": "en_attente"},
        )
        DemandeVisite.objects.get_or_create(
            annonce=by_titre["Villa avec jardin"],
            visiteur=visiteur2,
            defaults={"message": "Interesse par la villa, disponible cette semaine ?", "statut": "acceptee"},
        )

        SignalementAnnonce.objects.get_or_create(
            annonce=by_titre["Appartement deja loue"],
            utilisateur=visiteur1,
            defaults={"raison": "deja_louee", "message": "Cette annonce est deja louee depuis un mois.", "statut": "traite"},
        )
        SignalementAnnonce.objects.get_or_create(
            annonce=by_titre["Appartement vue palmeraie"],
            utilisateur=visiteur2,
            defaults={"raison": "prix_suspect", "message": "Le prix semble trop bas pour ce quartier.", "statut": "nouveau"},
        )

        self.stdout.write(self.style.SUCCESS("Donnees de demonstration pretes."))

    def _get_or_create_user(self, username, email, password, role, ville=""):
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        if created:
            user.set_password(password)
            user.save()
        user.profile.role = role
        if ville:
            user.profile.ville = ville
        user.profile.save()
        return user
