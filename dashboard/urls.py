from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name="panda-ledger-dashboard"),
    
]
