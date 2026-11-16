from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """New users get a profile. Superusers become Admins; everyone else is a Member."""
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={"role": Profile.Role.ADMIN if instance.is_superuser else Profile.Role.MEMBER},
        )
