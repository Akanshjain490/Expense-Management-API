"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from expenses.views import (
    hello_api,
    get_expenses,
    register,
    add_income,
    get_income,
    delete_income,
    update_income,
    patch_income,
    add_category,
    get_categories,
    update_category,
    patch_category,
    delete_category,
    monthly_report,
    set_budget,
    get_budget,
    update_budget,
    delete_budget,
    patch_budget,
    dashboard,

)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hello/', hello_api),
    path('api/expenses/', get_expenses),
    path('api/auth/register/', register),
    path('api/auth/login/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/income/', add_income),
    path('api/income/list/',get_income),
    path('api/income/delete/',delete_income),
    path('api/income/update/', update_income),
    path('api/income/patch/', patch_income),
    path('api/categories/', add_category),
    path('api/categories/list/', get_categories),
    path('api/categories/update/', update_category),
    path('api/categories/patch/', patch_category),
    path('api/categories/delete/', delete_category),
    path('api/reports/monthly/', monthly_report),
    path('api/budget/', set_budget),
    path('api/budget/details/', get_budget),
    path('api/budget/update/', update_budget),
    path('api/budget/delete/', delete_budget),
    path('api/budget/patch/', patch_budget),
    path('api/dashboard/', dashboard),
]


