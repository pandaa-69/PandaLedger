from django.urls import path
from . import views

urlpatterns = [
    path('analytics/dashboard/', views.portfolio_analytics, name='analytics_dashboard'),
    path('analytics/home-summary/', views.home_summary, name='home_summary'),
]