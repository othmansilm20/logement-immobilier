# Logement Immobilier

Plateforme web de gestion d'annonces immobilières développée avec **Django**. Elle met en relation des propriétaires qui publient des annonces et des visiteurs qui recherchent un logement, avec un espace administrateur pour modérer la plateforme.

## 🌐 Démo

🔗 **Application en ligne :** [Voir la démo](https://logement-immobilier.onrender.com)

## Fonctionnalités

### Espace visiteur
- Recherche et filtrage des annonces (ville, type de bien, prix, surface)
- Consultation détaillée d'une annonce avec carte interactive (Leaflet)
- Ajout aux favoris
- Demande de visite auprès du propriétaire
- Suivi de ses demandes de visite
- Signalement d'une annonce (fausse annonce, prix suspect, etc.)

### Espace propriétaire
- Tableau de bord avec statistiques (annonces publiées / en attente / brouillons)
- Création et modification d'annonces avec photos multiples et géolocalisation (recherche d'adresse + sélection sur carte)
- Gestion des demandes de visite reçues (acceptation / refus)

### Espace administrateur
- Tableau de bord global (utilisateurs, annonces, statistiques)
- Validation ou rejet des annonces soumises
- Gestion des utilisateurs (activation/désactivation, modification du rôle, réinitialisation de mot de passe)
- Traitement des signalements d'annonces

### Autres
- Authentification par e-mail, rôles distincts (visiteur / propriétaire / administrateur)
- Mode sombre
- Interface responsive (mobile / tablette / desktop)

## Stack technique

| Domaine | Techno |
|---|---|
| Backend | Django 6 |
| Frontend | HTML / CSS / JS vanilla (pas de framework JS) |
| Cartographie | Leaflet.js + tuiles Esri + géocodage Nominatim (OpenStreetMap) |
| Base de données (local) | SQL Server (via `mssql-django`) |
| Base de données (production / Render) | SQLite |
| Fichiers statiques en production | WhiteNoise |
| Serveur d'application | Gunicorn |

## Installation en local (Windows + SQL Server)

Prérequis : Python 3.13+, SQL Server (Express suffit) avec une instance nommée, driver **ODBC Driver 17 for SQL Server** installé.

```powershell
# 1. Environnement virtuel
python -m venv env
.\env\Scripts\Activate.ps1

# 2. Dépendances (inclut mssql-django + pyodbc)
pip install -r requirements-local.txt

# 3. Créer la base vide "LogementImmo" sur votre instance SQL Server
#    (via SSMS ou sqlcmd : CREATE DATABASE LogementImmo;)

# 4. Migrations + données de démonstration
python manage.py migrate
python manage.py seed_demo

# 5. Lancer le serveur
python manage.py runserver
```

La configuration de connexion à SQL Server se trouve dans `config/settings.py` (authentification Windows par défaut).

### Comptes de démonstration

| Rôle | Identifiant | Mot de passe |
|---|---|---|
| Administrateur | `admin@example.com` | `Admin1234` |
| Propriétaire | `karim@example.com` | `demo1234` |
| Propriétaire | `sara@example.com` | `demo1234` |
| Propriétaire | `nadia@example.com` | `demo1234` |
| Visiteur | `youssef@example.com` | `demo1234` |
| Visiteur | `imane@example.com` | `demo1234` |
| Visiteur | `amine@example.com` | `demo1234` |

## Déploiement sur Render

Le projet est prêt pour un déploiement direct sur [Render](https://render.com) via `render.yaml` (Blueprint) :

1. Pousser le dépôt sur GitHub.
2. Sur Render : **New > Blueprint**, sélectionner ce dépôt.
3. Render détecte `render.yaml`, exécute `build.sh` (installation des dépendances, `collectstatic`, migrations, seed) et démarre l'application avec Gunicorn.

**Particularité de cette configuration** : en production (détecté via la variable d'environnement `RENDER`, définie automatiquement par la plateforme), l'application bascule automatiquement sur **SQLite** au lieu de SQL Server. Le système de fichiers de Render étant éphémère, la base est **recréée à chaque déploiement** : les données sont donc systématiquement fraîches (utile pour une démo publique, mais toute donnée saisie par un visiteur entre deux déploiements n'est pas conservée durablement).

Pour redéployer manuellement les migrations + le jeu de données de démo :

```bash
python manage.py migrate
python manage.py seed_demo
```

La commande `seed_demo` est idempotente : la relancer ne crée jamais de doublons.

## Structure du projet

```
config/         # Réglages Django, URLs racine
accounts/       # Authentification, profils, rôles
properties/     # Annonces immobilières, photos, signalements
visits/         # Demandes de visite
favorites/      # Favoris des visiteurs
dashboard/      # Tableaux de bord (visiteur, propriétaire, admin)
frontend/       # Templates HTML
static/         # CSS / JS / images
media/          # Fichiers uploadés (photos d'annonces, avatars)
```

## Rôles et permissions

Le rôle métier (`visiteur` / `propriétaire` / `admin`) est stocké sur le modèle `Profile`, indépendamment des permissions techniques Django (`is_staff` / `is_superuser`). Toutes les vues d'administration sont protégées par un contrôle d'accès explicite.
