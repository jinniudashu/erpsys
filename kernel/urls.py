from django.urls import path
from .views import get_employees, get_menu_list

urlpatterns = [	
	# path('index_customer/', index_customer, name='index_customer'),
    path('getMenuList/', get_menu_list, name='get_menu_list'),
    path('get_employees/', get_employees, name='get_employees'),
]
