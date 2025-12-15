from django.urls import path
from . import views

urlpatterns = [
    path('api/expenses/', views.get_expenses, name='get_expenses'),
    path('api/expenses/add/', views.add_expense, name="add_expense"),
    
    
]
