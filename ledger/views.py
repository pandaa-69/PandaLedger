from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ledger import models
import json
from django.db.models import Sum
from django.utils import timezone


def get_expenses(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    expenses = models.Expense.objects.filter(user=request.user).order_by('-date')

    data = [{
        'id': e.id,
        'description': e.description,
        'amount': float(e.amount),
        'category': e.category.name if e.category else "Uncategorized",
        'date': e.date.strftime('%Y-%m-%d')
    } for e in expenses]

    return JsonResponse({'results': data})


def add_expense(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    data = json.loads(request.body)

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

    return JsonResponse({"message": "Expense added", "id": expense.id})


def delete_expense(request, id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'DELETE required'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    expense = get_object_or_404(models.Expense, id=id, user=request.user)
    expense.delete()

    return JsonResponse({'message': 'Deleted'})


def get_ledger_stats(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    today = timezone.now()
    expenses = models.Expense.objects.filter(
        user=request.user,
        date__month=today.month,
        date__year=today.year
    )

    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    budget = request.user.monthly_budget

    return JsonResponse({
        "total_spent": float(total_spent),
        "monthly_budget": float(budget),
        "remaining": float(budget - total_spent),
        "percentage": min(int((total_spent / budget) * 100), 100) if budget > 0 else 0
    })


def update_budget(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    data = json.loads(request.body)
    request.user.monthly_budget = float(data.get('budget', 0))
    request.user.save()

    return JsonResponse({"status": "success"})
