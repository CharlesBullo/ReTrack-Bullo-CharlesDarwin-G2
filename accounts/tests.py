from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile

User = get_user_model()
PW = "Str0ng-pass!"


def make_user(name, role=Profile.Role.MEMBER):
    u = User.objects.create_user(name, f"{name}@example.com", PW, first_name=name.title(), last_name="Test")
    if role != u.profile.role:
        u.profile.role = role
        u.profile.save()
    return u


class AccountTests(TestCase):
    def test_register_sets_user_type_hashes_password_and_rejects_duplicate_email(self):
        data = {"username": "newbie", "first_name": "New", "last_name": "User", "email": "new@example.com",
                "user_type": "staff", "password1": "Str0ng-pass!x", "password2": "Str0ng-pass!x"}
        self.assertRedirects(self.client.post(reverse("accounts:register"), data), reverse("accounts:login"))
        u = User.objects.get(username="newbie")
        self.assertNotEqual(u.password, "Str0ng-pass!x")
        self.assertEqual(u.profile.user_type, "staff")
        self.assertEqual(u.profile.role, Profile.Role.MEMBER)
        data.update(username="other", email="NEW@example.com")
        self.assertContains(self.client.post(reverse("accounts:register"), data), "already exists")

    def test_password_mismatch_rejected(self):
        data = {"username": "x1", "first_name": "A", "last_name": "B", "email": "x@example.com",
                "user_type": "student", "password1": "Str0ng-pass!x", "password2": "different"}
        self.assertEqual(self.client.post(reverse("accounts:register"), data).status_code, 200)
        self.assertFalse(User.objects.filter(username="x1").exists())

    def test_invalid_login_shows_error(self):
        make_user("mia")
        resp = self.client.post(reverse("accounts:login"), {"username": "mia", "password": "nope"})
        self.assertContains(resp, "Incorrect username or password")

    def test_logged_out_users_are_sent_to_login(self):
        for name in ["dashboard", "member_dashboard", "admin_dashboard", "profile", "profile_edit"]:
            url = reverse(f"accounts:{name}")
            self.assertRedirects(self.client.get(url), f"{reverse('accounts:login')}?next={url}")

    def test_role_dashboards_are_isolated(self):
        make_user("mia")
        make_user("ada", Profile.Role.ADMIN)
        self.client.login(username="mia", password=PW)
        self.assertRedirects(self.client.get(reverse("accounts:dashboard")), reverse("accounts:member_dashboard"))
        self.assertRedirects(self.client.get(reverse("accounts:admin_dashboard")), reverse("accounts:member_dashboard"))
        self.client.logout()
        self.client.login(username="ada", password=PW)
        self.assertRedirects(self.client.get(reverse("accounts:dashboard")), reverse("accounts:admin_dashboard"))
        self.assertRedirects(self.client.get(reverse("accounts:member_dashboard")), reverse("accounts:admin_dashboard"))

    def test_logout_requires_post_and_ends_session(self):
        make_user("mia")
        self.client.login(username="mia", password=PW)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.client.post(reverse("accounts:logout"))
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 302)

    def test_profile_update_cannot_change_role(self):
        mia = make_user("mia")
        self.client.login(username="mia", password=PW)
        resp = self.client.post(reverse("accounts:profile_edit"), {
            "first_name": "Mia", "last_name": "Reyes", "email": "mia2@example.com",
            "user_type": "student", "school_id": "2024-001", "phone": "+63 912 345 6789", "role": "admin"})
        self.assertRedirects(resp, reverse("accounts:profile"))
        mia.refresh_from_db()
        self.assertEqual(mia.email, "mia2@example.com")
        self.assertEqual(mia.profile.role, Profile.Role.MEMBER)
