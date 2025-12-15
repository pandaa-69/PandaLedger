from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ledger import models

# @login_required #only logged in users can see thier data 

def get_expenses(request):

    #first we need to get the data from the db for this user and only this user so that there is no security issue and no other can access others users 

    # expenses = models.Expense.objects.filter(user=request.user)
    
    
    expenses = models.Expense.objects.all()

    data = []

    for expense in expenses:
        item = {
            'id':expense.id,
            'description':expense.description,
            'amount':float(expense.amount),
            'category':expense.category.name if expense.category else "Uncategorized",
            'date': expense.date.strftime('%Y-%m-%d')
        }
        data.append(item)

    # returning the json formate of the list of data
    return JsonResponse({'results': data})

