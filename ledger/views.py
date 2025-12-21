from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from ledger import models # We use models.Expense
import json
from django.contrib.auth import get_user_model
# 👇 NEW IMPORTS (Required for Math & Dates)
from django.db.models import Sum
from django.utils import timezone

@login_required 
def get_expenses(request):
    # 1. Get the raw data from DB
    expenses = models.Expense.objects.filter(user=request.user).order_by('-date')

    # 2. Create a clean list
    data = []
    for expense in expenses:
        item = {
            'id': expense.id,
            'description': expense.description,
            'amount': float(expense.amount),
            'category': expense.category.name if expense.category else "Uncategorized",
            'date': expense.date.strftime('%Y-%m-%d')
        }
        data.append(item)

    return JsonResponse({'results': data})

@csrf_exempt
def add_expense(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        data = json.loads(request.body)
        category_obj, created = models.Category.objects.get_or_create(
            name = data["category"],
            user = request.user
        )
        
        new_expense = models.Expense.objects.create(
            user=request.user,
            amount=data["amount"],
            description=data["description"],
            category=category_obj,
            date=data["date"]
        )

        return JsonResponse({
            "message": "Expense Added Successfully",
            "id": new_expense.id
        })
    
@csrf_exempt
def delete_expense(request, id):
    if request.method=='DELETE':    
        if not request.user.is_authenticated:
            return JsonResponse ({'error': 'Unauthorized'}, status = 401)
        
        expense = get_object_or_404(models.Expense, id=id, user=request.user)
        expense.delete()
        
        return JsonResponse({'message': 'Expense deleted succesfully'})
    return JsonResponse({'error': 'Method not allowed'}, status = 405)

# 1. Get Ledger Stats (Spent vs Budget) 📊
@login_required
def get_ledger_stats(request):
    today = timezone.now()
    
    # Filter expenses for the current month & year
    current_month_expenses = models.Expense.objects.filter( # 👈 Fixed: models.Expense
        user=request.user,
        date__month=today.month,
        date__year=today.year
    )
    
    # Calculate Total Spent
    total_spent = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get User's Budget from DB
    budget = request.user.monthly_budget
    
    return JsonResponse({
        "total_spent": float(total_spent),
        "monthly_budget": float(budget),
        "remaining": float(budget) - float(total_spent),
        # Prevent division by zero logic
        "percentage": min(int((total_spent / budget) * 100), 100) if budget > 0 else 0
    })

# 2. Update Budget (Edit Limit) ✏️
@csrf_exempt
@login_required
def update_budget(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_budget = float(data.get('budget', 0))
            
            # Save to the User Model
            request.user.monthly_budget = new_budget
            request.user.save()
            
            return JsonResponse({"status": "success", "new_budget": new_budget})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({'error': 'POST method required'}, status=405)