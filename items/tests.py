from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Item


class ReportItemTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("juan", password="pass12345!")
        self.cat = Category.objects.create(name="Wallet")
        self.data = {"title": "Black wallet", "category": self.cat.pk, "location": "Library 2F",
                     "event_date": date.today().isoformat()}

    def test_login_required(self):
        r = self.client.get(reverse("items:create", args=["lost"]))
        self.assertEqual(r.status_code, 302)

    def test_create_sets_kind_and_reporter(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse("items:create", args=["found"]), self.data)
        item = Item.objects.get()
        self.assertRedirects(r, item.get_absolute_url())
        self.assertEqual((item.kind, item.reporter), ("found", self.user))

    def test_bad_kind_404(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("items:create", args=["stolen"])).status_code, 404)