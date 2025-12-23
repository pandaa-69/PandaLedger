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
from .utils import send_email_async 

@ensure_csrf_cookie
def signup_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            User = get_user_model()
            
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            # 1. Validation: Ensure all fields are present
            if not username or not password or not email:
                return JsonResponse({'error': 'All fields (Username, Email, Password) are required.'}, status=400)

            # 2. Validation: Check if email is already taken
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'This email is already registered.'}, status=400)

            # 3. Create User with Email
            user = User.objects.create_user(
                username=username,
                email=email, # 👈 Save the email here
                password=password
            )
            
            return JsonResponse({
                'message': 'User created succesfully',
                'id': user.id
            })

        except IntegrityError:
            # This catches duplicate usernames
            return JsonResponse({'error': 'Username already taken'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'GET method not allowed. Please use POST.'}, status=405)



@ensure_csrf_cookie
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





def user_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

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
            User = get_user_model()

            if 'email' in data:
                new_email = data['email']
                if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                    return JsonResponse(
                        {"error": "This email is already in use."},
                        status=400
                    )
                user.email = new_email

            if data.get('new_password'):
                user.set_password(data['new_password'])
                user.save()
                update_session_auth_hash(request, user)
            else:
                user.save()

            return JsonResponse({"message": "Profile updated successfully!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)





def request_password_reset(request):
    """
    Takes an email, finds the user, and sends a reset link ASYNCHRONOUSLY.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            User = get_user_model()

            # 1. Find the user (Fail silently if not found for security)
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # We return success even if user doesn't exist so hackers can't fish for emails
                return JsonResponse({"message": "If an account exists, a reset link has been sent."})

            # 2. Generate the Token and UID manually
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # 3. Construct the Link (Point to your Frontend Domain!)
            # Note: Ensure this matches your React Route
            reset_link = f"https://pandaledger.tech/reset-password/{uid}/{token}"

            # 4. Prepare Email Data
            email_data = {
                'subject': "Reset Your PandaLedger Password",
                'body': f"Hi {user.username},\n\nYou requested a password reset.\nClick the link below to set a new password:\n\n{reset_link}\n\nIf you didn't ask for this, please ignore this email.",
                'to': user.email
            }

            # 5. Send Async (Instant Return) 🚀
            send_email_async(email_data)

            return JsonResponse({"message": "If an account exists, a reset link has been sent."})
                
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