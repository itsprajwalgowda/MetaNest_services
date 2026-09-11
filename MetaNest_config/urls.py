"""
URL configuration for MetaNest_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
#from rest_framework import permissions
#from drf_yasg.views import get_schema_view
#from drf_yasg import openapi
from django.views.generic import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),


    path(
        "api/v1/auth/",
        include("apps.authentication.urls"),
    ),

    path(
        "api/v1/finance/",
        include("apps.finance.urls"),
    ),

    path("api/v1/dashboard/", include("apps.dashboard.urls")),

    path(
        "api/v1/admin/users/",
        include("apps.administration.urls"),
    ),

    path(
    "",
    RedirectView.as_view(url="/swagger/", permanent=False),
    ),
    
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

path(
    "swagger/",
    SpectacularSwaggerView.as_view(url_name="schema"),
    name="swagger-ui",
),

path(
    "redoc/",
    SpectacularRedocView.as_view(url_name="schema"),
    name="redoc",
),
path(
    "api/v1/apartment-master/",
    include("apps.apartment_master.urls"),
),
]
