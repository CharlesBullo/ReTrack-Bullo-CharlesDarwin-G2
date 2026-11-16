from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    class UserType(models.TextChoices):
        STUDENT = "student", "Student"
        STAFF = "staff", "Staff member"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    user_type = models.CharField("I am a", max_length=10, choices=UserType.choices, default=UserType.STUDENT)
    school_id = models.CharField("School / staff ID", max_length=30, blank=True)
    phone = models.CharField(
        "Contact number",
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\+?[0-9 ()-]{7,20}$", "Enter a valid contact number, for example +63 912 345 6789.")],
    )
    photo = models.ImageField("Profile photo", upload_to="profile_photos/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def initial(self):
        return (self.user.first_name or self.user.username)[:1].upper()
