from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
import json 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

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
        
@csrf_exempt
def logout_api(request):
    if request.method =='POST':
        logout(request) #this kills the session/cookie for the current user
        return JsonResponse({
            'message':'Logged out successfully',
        })
    return JsonResponse({
        'error':'Method not allowed'},
        status = 405
    )



@csrf_exempt
@login_required
def user_profile(request):
    """
    GET: Returns user details (username, email, join date)
    PUT: Updates email and password
    """
    if request.method == 'GET':
        return JsonResponse({
            "username": request.user.username,
            "email": request.user.email,
            "date_joined": request.user.date_joined.strftime("%b %d, %Y")
        })

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # 1. Update Email
            if 'email' in data:
                user.email = data['email']
            
            # 2. Update Password (if provided)
            if 'new_password' in data and data['new_password']:
                user.set_password(data['new_password'])
                user.save()
                # Important: This keeps the user logged in after password change
                update_session_auth_hash(request, user) 
            else:
                user.save()
                
            return JsonResponse({"message": "Profile updated successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)