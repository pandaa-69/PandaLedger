from pathlib import Path
import os 
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['pandaledger-api.onrender.com', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
    'portfolio',
    'dashboard',
    'ledger',
    'analytics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Keep at the top
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- 🛡️ CRITICAL PRODUCTION SECURITY SETTINGS ---

# 1. Proxy Trust (For Render)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 2. CORS (For Handshake)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False 
CORS_ALLOWED_ORIGINS = [
    "https://panda-ledger.vercel.app",
    "http://localhost:5173",
]
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']

# 3. CSRF Trusted Origins (The Triple Lock)
CSRF_TRUSTED_ORIGINS = [
    "https://panda-ledger.vercel.app",
    "https://pandaledger-api.onrender.com",
]

# This is the "secret" setting that stops 403 Forbidden on Render
CSRF_ALLOWED_ORIGINS = [
    "https://panda-ledger.vercel.app",
]

CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN" # Case-sensitive for middleware

# 4. Cookie Settings (Must match exactly)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Allows your csrf.js to read it
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'None' # Crucial for different domains
SESSION_COOKIE_SAMESITE = 'None'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
ROOT_URLCONF = 'PandaLedger.urls'

# --- 🏢 TEMPLATES, DB, & OTHER SETTINGS ---

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PandaLedger.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER':os.getenv('DB_USER'),
        'PASSWORD':os.getenv('DB_PASSWORD'),
        'HOST':os.getenv('DB_HOST'),
        'PORT':os.getenv("DB_PORT"),
    }
}

if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

CACHES = {
    'default':{
        'BACKEND':'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION':'unique-snowflake',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.CustomUser'
LOGIN_URL = '/api/auth/login/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER