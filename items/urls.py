from django.urls import path

from . import views

app_name = "items"

urlpatterns = [
    path("items/report/<str:kind>/", views.item_create, name="create"),
    path("items/<int:pk>/", views.item_detail, name="detail"),
]