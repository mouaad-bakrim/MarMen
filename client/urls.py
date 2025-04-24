from django.urls import path
from .views import ajouter_client

urlpatterns = [
    path('ajouter/', ajouter_client, name='ajouter_client'),
]
