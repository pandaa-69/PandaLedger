from django.urls import path
from . import views

urlpatterns = [
    path('api/expenses/', views.get_expenses, name='get_expenses'),
    
]
