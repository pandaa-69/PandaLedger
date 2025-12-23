"""
URL configuration for PandaLedger project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from portfolio.views import wake_up

# Auto-create a superuser for Render Free Tier
User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('panda', 'panda@example.com', 'panda@69')
        print("Superuser created successfully!")
except Exception:
    pass


urlpatterns = [
    path('admin/', admin.site.urls),
    path('wakeup/', wake_up, name = 'wakeup'),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/', include('ledger.urls')),
    path('api/', include('core.urls')),
    path('api/', include('dashboard.urls')),
    path('api/', include('analytics.urls')),
]
