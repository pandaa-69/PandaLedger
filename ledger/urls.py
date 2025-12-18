from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.get_expenses, name='get_expenses'),
    path('expenses/add/', views.add_expense, name="add_expense"),
    path('expenses/delete/<int:id>', views.delete_expense, name="delete_expense"),
]
