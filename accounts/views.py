from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import LoginForm, ProfileForm, RegistrationForm, UserUpdateForm
from .models import Profile
from .utils import get_profile

User = get_user_model()


def home(request):
    return redirect("accounts:dashboard" if request.user.is_authenticated else "accounts:login")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # password hashed by UserCreationForm
            messages.success(request, "Your account is ready. Log in to continue.")
            return redirect("accounts:login")
        messages.error(request, "We couldn't create your account. Fix the highlighted fields.")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return reverse("accounts:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        messages.success(self.request, f"Welcome back, {user.first_name or user.username}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Login failed. Check your username and password.")
        return super().form_invalid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You've been logged out.")
    return redirect("accounts:login")


@login_required
def dashboard_redirect(request):
    """Send each user to the dashboard for their role."""
    if get_profile(request.user).is_admin_role:
        return redirect("accounts:admin_dashboard")
    return redirect("accounts:member_dashboard")


@role_required(Profile.Role.ADMIN)
def admin_dashboard(request):
    members = User.objects.filter(profile__role=Profile.Role.MEMBER)
    context = {
        "member_count": members.count(),
        "new_this_month": members.filter(date_joined__gte=timezone.now() - timedelta(days=30)).count(),
        "admin_count": User.objects.filter(profile__role=Profile.Role.ADMIN).count(),
        "recent_members": members.select_related("profile").order_by("-date_joined")[:8],
    }
    return render(request, "accounts/admin_dashboard.html", context)


@role_required(Profile.Role.MEMBER)
def member_dashboard(request):
    return render(request, "accounts/member_dashboard.html", {"profile": get_profile(request.user)})


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"profile": get_profile(request.user)})


@login_required
def profile_edit(request):
    profile = get_profile(request.user)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
        messages.error(request, "Your changes weren't saved. Fix the highlighted fields.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    return render(request, "accounts/profile_edit.html", {"user_form": user_form, "profile_form": profile_form})
