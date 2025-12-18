from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
import json 

@csrf_exempt
def signup_api(request):
    if request.method=='POST':
        data = json.loads(request.body)
        User = get_user_model()

        try:
            # Creating the user using the Custom user model

            user = User.objects.create_user(
                username=data['username'],
                password=data['password']
            )
            return JsonResponse({
                'message': 'User created succesfully',
                'id': user.id
            })
        except IntegrityError:
            return JsonResponse({
                'error':'Username already taken'}, status = 400)
    return JsonResponse({'error': 'GET method not allowed. Please use POST.'}, status=405)
        
@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'message': 'Login succesful',
                'username':user.username or "Commander"
            })
        else:
            return JsonResponse ({'error':'Invalid credentials'}, status = 400)
    return JsonResponse({'error': 'GET method not allowed. Please use POST.'}, status=405)
        
