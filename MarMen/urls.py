from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^', include(('base.urls', 'base'), namespace="base")),
    re_path(r'^', include(('client.urls', 'client'), namespace="invoice")),
    re_path(r'^', include(('order.urls', 'order'), namespace="invoice")),
    re_path(r'^', include(('produit.urls', 'produit'), namespace="invoice")),

]