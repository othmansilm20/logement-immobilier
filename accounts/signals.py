from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def creer_profile_utilisateur(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def sauvegarder_profile_utilisateur(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()