import logging
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from ledger import models

logger = logging.getLogger(__name__)

@require_GET
def get_expenses(request):
    """
    API: Returns a list of user's expenses, ordered by date.
    Authentication Required.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        expenses = models.Expense.objects.filter(user=request.user).order_by('-date')

        data = [{
            'id': e.id,
            'description': e.description,
            'amount': float(e.amount),
            'category': e.category.name if e.category else "Uncategorized",
            'date': e.date.strftime('%Y-%m-%d')
        } for e in expenses]

        return JsonResponse({'results': data})
    except Exception as e:
        logger.error(f"Error fetching expenses for {request.user.username}: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to fetch expenses'}, status=500)


@require_POST
def add_expense(request):
    """
    API: Adds a new expense.
    Creates a new Category if it doesn't exist.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
        
        # Validation
        if not all(k in data for k in ["amount", "description", "date", "category"]):
             return JsonResponse({'error': 'Missing required fields'}, status=400)

        category, _ = models.Category.objects.get_or_create(
            name=data["category"],
            user=request.user
        )

        expense = models.Expense.objects.create(
            user=request.user,
            amount=data["amount"],
            description=data["description"],
            category=category,
            date=data["date"]
        )
        
        logger.info(f"Expense added for {request.user.username}: {expense.amount} on {expense.date}")
        return JsonResponse({"message": "Expense added", "id": expense.id})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error adding expense: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to add expense'}, status=500)


@require_http_methods(["DELETE"])
def delete_expense(request, id):
    """
    API: Deletes an expense by ID.
    User owns checks included.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        expense = get_object_or_404(models.Expense, id=id, user=request.user)
        expense.delete()
        logger.info(f"Expense {id} deleted by {request.user.username}")
        return JsonResponse({'message': 'Deleted'})
    except Exception as e:
         logger.error(f"Error deleting expense {id}: {e}", exc_info=True)
         return JsonResponse({'error': 'Failed to delete'}, status=500)


@require_GET
def get_ledger_stats(request):
    """
    API: Returns monthly spending stats vs budget.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        today = timezone.now()
        expenses = models.Expense.objects.filter(
            user=request.user,
            date__month=today.month,
            date__year=today.year
        )

        total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        budget = getattr(request.user, 'monthly_budget', 0) # Safe access

        return JsonResponse({
            "total_spent": float(total_spent),
            "monthly_budget": float(budget),
            "remaining": float(budget - total_spent),
            "percentage": min(int((total_spent / budget) * 100), 100) if budget > 0 else 0
        })
    except Exception as e:
        logger.error(f"Error fetching stats for {request.user.username}: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to fetch stats'}, status=500)


@require_POST
def update_budget(request):
    """
    API: Updates the user's monthly budget.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        new_budget = float(data.get('budget', 0))
        
        if new_budget < 0:
             return JsonResponse({'error': 'Budget cannot be negative'}, status=400)

        request.user.monthly_budget = new_budget
        request.user.save()
        
        logger.info(f"Budget updated for {request.user.username} to {new_budget}")
        return JsonResponse({"status": "success"})
    except ValueError:
        return JsonResponse({'error': 'Invalid budget amount'}, status=400)
    except Exception as e:
        logger.error(f"Error updating budget: {e}", exc_info=True)
        return JsonResponse({'error': 'Failed to update budget'}, status=500)

