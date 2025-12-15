from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from ledger import models
import json
from django.contrib.auth import get_user_model

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

@csrf_exempt
def add_expense(request):
    # converting the Raw data coming from frontend 
    if request.method == 'POST':
        data = json.loads(request.body)

        # getting the custom User model 
        User = get_user_model()

        # get the admin user ID = 1 this is my superuser 
        # i am hardcoding this for now until we build the login  system 

        admin_user = User.objects.get(id=1)

        # nwo we will create the object in the Db 
        new_expense = models.Expense.objects.create(
            user=admin_user,
            amount = data["amount"],
            description=data["description"],
            category = models.Category.objects.get(name=data["category"]),
            date = data["date"]
        )

        # sending a confirmation to frontend of the process being completed
        return JsonResponse({
            "message": "Expense Added Succesfully",
            "id":new_expense.id
        })