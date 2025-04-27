from django.urls import path
from . import views


urlpatterns = [
    path('vente/', views.add_order, name='add_order'),
    path('order/devis', views.Devis_direct.as_view(), name='devis'),
    path('direct/devis/detail/<int:pk>/', views.DetailDevisDirect.as_view(),
         name='Detail_devis_direct'),
    path('invoicebondevisdirect/<int:pk>/print/', views.invoice_bondevis_direct_pdf_view,
         name='printInvoivebondevisdirect'),
    path('direct_devis/<int:pk>/conf/', views.commande_conf, name='commande_conf'),

]
