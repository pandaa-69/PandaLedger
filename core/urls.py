from django.urls import path
from . import views


urlpatterns = [
    path('auth/signup/', views.signup_api, name='signup_api'),
    path('auth/login/', views.login_api, name='login_api'),
    path('auth/logout/', views.logout_api, name='logout_api'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('auth/reset-password/', views.request_password_reset, name='reset_password'),
    path('auth/reset-password-confirm/', views.reset_password_confirm, name='reset_password_confirm'),
    path('auth/csrf/', views.get_csrf_token, name='get_csrf_token'),

]
