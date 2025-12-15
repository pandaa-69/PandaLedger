from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="panda-ledger-home"),
    path('about/', views.about, name='panda-ledger-about'),
    
]
