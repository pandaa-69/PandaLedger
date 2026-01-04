"""
Define URL routing for the Portfolio application.
Handles asset search, portfolio management, and administrative seeding.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Asset Management
    path('search/', views.search_asset),

    # Portfolio & Holdings
    path('holdings/', views.get_portfolio),
    path('holdings/<int:asset_id>/', views.get_holding_details),

    # Transactions
    path('transaction/add/', views.add_transaction),
    path('transaction/delete/<int:transaction_id>/', views.delete_transaction),

    # Administration (Protected by Superuser Check)
    path('secret-seed-db/', views.seed_db_view, name='secret-seed'),
]