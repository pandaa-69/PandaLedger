from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/live/', views.market_dashboard_api, name="panda-ledger-dashboard"),
    
]
