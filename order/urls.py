from django.urls import path
from . import views


urlpatterns = [
    path('vente/', views.add_order, name='add_order'),
    path('order/devis', views.Devis_direct.as_view(), name='devis')
]
