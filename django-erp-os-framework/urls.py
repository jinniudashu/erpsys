from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from kernel.admin import applications_site

from .views import login_view, logout_view, get_user_info, get_perm_code, get_menu_list

urlpatterns = [
    path(f'{settings.CUSTOMER_SITE_NAME}/', applications_site.urls),
    path('admin/', admin.site.urls),
    path('applications/', applications_site.urls),
    # path('login/', login_view, name='login'),
    # path('logout/', logout_view, name='logout'),
    # path('getUserInfo/', get_user_info, name='getUserInfo'),
    # path('getPermCode/', get_perm_code, name = 'getPermCode'),
    # path('getMenuList/', get_menu_list, name='getMenuList'),
]
