from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),                 # API routes from your app
    path("api-auth/", include("rest_framework.urls")),  # DRF login/logout
    path("api/token/", TokenObtainPairView.as_view()),  # JWT obtain
    path("api/token/refresh/", TokenRefreshView.as_view()),
]
