from django.contrib import admin
from django.urls import path
from maor.admin import maor_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('maor/', maor_site.urls),
]
