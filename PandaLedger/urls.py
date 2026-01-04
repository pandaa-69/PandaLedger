import logging
import os
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
from portfolio.views import wake_up

# Load the .env file here to ensure environment variables are present before the app boots.
load_dotenv()

logger = logging.getLogger(__name__)

# Auto-provision a superuser if the credentials are in the environment.
# This makes cold-starts on new deployments seamless.
User = get_user_model()
try:
    SU_USERNAME = os.getenv('DJANGO_SUPERUSER_USERNAME')
    SU_EMAIL = os.getenv('DJANGO_SUPERUSER_EMAIL')
    SU_PASSWORD = os.getenv('DJANGO_SUPERUSER_PASSWORD')

    if SU_PASSWORD:
        if not User.objects.filter(username=SU_USERNAME).exists():
            logger.info(f"Creating Superuser: {SU_USERNAME}...")
            User.objects.create_superuser(SU_USERNAME, SU_EMAIL, SU_PASSWORD)
            logger.info("Superuser created successfully.")
        else:
            logger.info("Superuser already exists. Skipping creation.")
    else:
        logger.warning("No Superuser Password found in environment. Skipping creation.")

except Exception as e:
    logger.error(f"Error creating superuser: {e}")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('wakeup/', wake_up, name='wakeup'),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/', include('ledger.urls')),
    path('api/', include('core.urls')),
    path('api/', include('dashboard.urls')),
    path('api/', include('analytics.urls')),
]