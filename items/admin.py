from django.contrib import admin

from .models import Category, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "category", "status", "reporter", "event_date")
    list_filter = ("kind", "status", "category")
    search_fields = ("title", "location", "reporter__username")


admin.site.register(Category)