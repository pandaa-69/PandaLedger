from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_asset),
    path('holdings/', views.get_portfolio),
    path('holdings/<int:asset_id>/', views.get_holding_details),
    path('transaction/delete/<int:transaction_id>/', views.delete_transaction),
    path('transaction/add/', views.add_transaction),
    path('secret-seed-db/', views.seed_db_view, name='secret-seed'),
]