from django.urls import path
from .views import get_employees

urlpatterns = [	
	# path('index_customer/', index_customer, name='index_customer'),
    path('get_employees/', get_employees, name='get_employees'),
]
