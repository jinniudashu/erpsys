from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# URL：127.0.0.1/api/token/
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

# URL：127.0.0.1/api/token/refresh/
class CustomTokenRefreshView(TokenRefreshView):
    pass
