from django.urls import path
from . import views


urlpatterns = [
    path('auth/signup/', views.signup_api, name='signup_api'),
    path('auth/login/', views.login_api, name='login_api'),

]
