from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.market_dashboard_api, name="panda-ledger-dashboard"),
    
]
