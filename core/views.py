from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
import json 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator


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



def request_password_reset(request):
    """
    Takes an email, finds the user, and sends a reset link (to console).
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            # Django Form handles the heavy lifting (finding user, generating token)
            form = PasswordResetForm({'email': email})
            if form.is_valid():
                # This saves the email content to the console
                form.save(
                    request=request,
                    use_https=False,
                    from_email='support@pandaledger.com', 
                    email_template_name='registration/password_reset_email.html',
                    domain_override='127.0.0.1:5173'
                )
                return JsonResponse({"message": "If an account exists, a reset link has been sent."})
            else:
                return JsonResponse({"error": "Invalid email"}, status=400)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)



def reset_password_confirm(request):
    """
    Validates the UID/Token and sets the new password.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uid = data.get('uid')
            token = data.get('token')
            new_password = data.get('new_password')
            
            # 1. Decode the User ID
            try:
                user_id = force_str(urlsafe_base64_decode(uid))
                User = get_user_model()
                user = User.objects.get(pk=user_id)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return JsonResponse({"error": "Invalid user link"}, status=400)
            
            # 2. Check the Token (Is it valid? Is it expired?)
            if default_token_generator.check_token(user, token):
                # 3. Success! Change Password
                user.set_password(new_password)
                user.save()
                return JsonResponse({"message": "Password has been reset successfully."})
            else:
                return JsonResponse({"error": "Link is invalid or expired"}, status=400)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)


@ensure_csrf_cookie
def get_csrf_token(request):
    """
    This view does nothing but set the CSRF cookie.
    React calls this when the app loads.
    """
    return JsonResponse({'message': 'CSRF cookie set'})