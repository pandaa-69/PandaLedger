from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import get_user_model
from portfolio.views import wake_up
import os 
from dotenv import load_dotenv

# 1. Load the .env from the base directory (if running locally)
# This looks for .env in the parent folders automatically
load_dotenv()

# 2. Auto-create Superuser (Securely)
User = get_user_model()
try:
    # Get credentials from .env or Render Dashboard
    SU_USERNAME = os.getenv('DJANGO_SUPERUSER_USERNAME')
    SU_EMAIL = os.getenv('DJANGO_SUPERUSER_EMAIL')
    SU_PASSWORD = os.getenv('DJANGO_SUPERUSER_PASSWORD')

    # Only run if we actually have a password set (safety check)
    if SU_PASSWORD:
        if not User.objects.filter(username=SU_USERNAME).exists():
            print(f"👤 Creating Superuser: {SU_USERNAME}...")
            User.objects.create_superuser(SU_USERNAME, SU_EMAIL, SU_PASSWORD)
            print("✅ Superuser created successfully!")
        else:
            print("ℹ️ Superuser already exists. Skipping.")
    else:
        print("⚠️ No Superuser Password found in Env. Skipping creation.")

except Exception as e:
    print(f"❌ Error creating superuser: {e}")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('wakeup/', wake_up, name='wakeup'),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/', include('ledger.urls')),
    path('api/', include('core.urls')),
    path('api/', include('dashboard.urls')),
    path('api/', include('analytics.urls')),
]