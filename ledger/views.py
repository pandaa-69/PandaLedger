from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from ledger import models
import json
from django.contrib.auth import get_user_model

# @login_required #only logged in users can see thier data 

@login_required 
def get_expenses(request):
    # 1. Get the raw data from DB
    expenses = models.Expense.objects.filter(user=request.user).order_by('-date') # Added order_by to show newest first!

    # 2. Create a clean list manually (THIS FIXES THE DISPLAY)
    data = []
    for expense in expenses:
        item = {
            'id': expense.id,
            'description': expense.description,
            'amount': float(expense.amount),
            # This handles the "Uncategorized" case safely
            'category': expense.category.name if expense.category else "Uncategorized",
            # This formats the date to be nice and short
            'date': expense.date.strftime('%Y-%m-%d')
        }
        data.append(item)

    return JsonResponse({'results': data})



@csrf_exempt
def add_expense(request):
    if request.method == 'POST':
        # 1. Check if user is actually logged in
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        data = json.loads(request.body)
        # we need to get or create the category cause if there is a new user then we need in the start we need to  make new categories for the table 
        category_obj, created = models.Category.objects.get_or_create(
            name = data["category"],
            user = request.user
        )
        
        # 2. Use request.user (The actual logged-in user!)
        new_expense = models.Expense.objects.create(
            user=request.user,  # <--- CHANGED THIS
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
        # getting the expense , but only if it belongs to this user 
        expense = get_object_or_404(models.Expense, id=id, user=request.user)

        expense.delete()
        
        return JsonResponse({'message': 'Expense deleted succesfully'})
    return JsonResponse({'error': 'Method not allowed'}, status = 405)
