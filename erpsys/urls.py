from django.contrib import admin
from django.urls import path
from applications.admin import applications_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('applications/', applications_site.urls),
]
