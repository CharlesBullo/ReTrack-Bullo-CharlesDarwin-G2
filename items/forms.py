from django import forms
from django.utils import timezone

from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["title", "category", "description", "location", "event_date", "photo"]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_event_date(self):
        d = self.cleaned_data["event_date"]
        if d > timezone.localdate():
            raise forms.ValidationError("The date can't be in the future.")
        return d

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Photo must be 5 MB or smaller.")
        return photo