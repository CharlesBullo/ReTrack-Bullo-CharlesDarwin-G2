from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profile

User = get_user_model()
MAX_PHOTO_BYTES = 2 * 1024 * 1024


class EmailRulesMixin:
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("An account with this email already exists.")
        domain = settings.RETRACK_EMAIL_DOMAIN.lower().lstrip("@")
        if domain and not email.endswith("@" + domain):
            raise forms.ValidationError(f"Use your school email address (ending in @{domain}).")
        return email


class RegistrationForm(EmailRulesMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    user_type = forms.ChoiceField(label="I am a", choices=Profile.UserType.choices)

    field_order = ["username", "first_name", "last_name", "email", "user_type", "password1", "password2"]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.user_type = self.cleaned_data["user_type"]
            user.profile.save()
        return user


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Incorrect username or password. Check both and try again.",
        "inactive": "This account is inactive. Contact an admin.",
    }


class UserUpdateForm(EmailRulesMixin, forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("user_type", "school_id", "phone", "photo")  # role is not editable
        widgets = {"photo": forms.ClearableFileInput(attrs={"accept": "image/*"})}

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "size") and photo.size > MAX_PHOTO_BYTES:
            raise forms.ValidationError("Photo must be 2 MB or smaller.")
        return photo
