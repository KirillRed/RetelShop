"""
Django settings for RetelShop project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import google_auth_oauthlib.flow
import os

from decouple import config

import socket

import pyrebase

from django.urls import reverse_lazy


from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.105',
    'apiretelshop.loca.lt',
    'apiretelshopik.loca.lt',
    'apiretelshops.loca.lt',
    'retelshop.loca.lt',
    'localhost:4200',
    'apretelshop.loca.lt',
    'retelshopik.loca.lt',
    'localhost:2753'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'phonenumber_field',
    'channels',
    'webpush',
    'rest_framework.authtoken',
    'eav',
    'social_django',
    'sslserver',

    'shop.apps.ShopConfig',
    'registration.apps.RegistrationConfig',
    'chat.apps.ChatConfig',
    'notifications.apps.NotificationsConfig',
]

import django.middleware.csrf

django.middleware.csrf.CsrfViewMiddleware.async_capable = False

MIDDLEWARE = [
    #'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'shop.middleware.HeadersMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',


]

ROOT_URLCONF = 'RetelShop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [r'F:/RetelShop'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

PYTHONWARNINGS = "ignore:Unverified HTTPS request"


CSRF_TRUSTED_ORIGINS = ['localhost:4200',
                        'retelshop.loca.lt', 'localhost:2753', 'localhost:8000']

CHATTERBOT = {
    'name': 'Django ChatterBot Example',
    'django_app_name': 'django_chatterbot'
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': r'F:\RetelShop\shop\log.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'CRITICAL',
            'propagate': True,
        },
        'shop.views': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'registration.views': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}


flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'F://Retelshop/Retelshop/client_secret.json',
    scopes=['email', 'name', 'photoUrl'])

flow.redirect_uri = 'https://www.example.com/oauth2callback'


authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'registration.email_backend.EmailBackend'
)

WSGI_APPLICATION = 'RetelShop.wsgi.application'

ASGI_APPLICATION = 'RetelShop.routing.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbshop',
        'USER': 'postgres',
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": """MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEZx8gdSsKScUj/q1vq+hw58RhWBN1L4swpmIiOzZZDHGWD9j4dSvzVsViQqvklQaFnEZCJ1nTO0DINUURo5YTYA==""",
    "VAPID_PRIVATE_KEY": config('VAPID_PRIVATE_KEY'),
    "VAPID_ADMIN_EMAIL": config('MY_EMAIL')
}

firebaseConfig = {
    'apiKey': config('FIREBASE_API_KEY'),
    'authDomain': "retelshop-6c5fb.firebaseapp.com",
    'databaseURL': "https://retelshop-6c5fb.firebaseio.com",
    'projectId': "retelshop-6c5fb",
    'storageBucket': "retelshop-6c5fb.appspot.com",
    'messagingSenderId': "427793445340",
    'appId': config('firebaseappId'),
    'measurementId': "G-51H3VJ0FQ3"
}

firebase = pyrebase.initialize_app(firebaseConfig)


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static\\')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_dev')
]

MEDIA_URL = '/images/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'images\\')

SUPPORTED_IMAGE_EXTENSIONS = ['jpeg', 'jpg', 'bmp', 'gif', 'png', 'webp']

MIN_PRODUCT_IMAGE_RESOLUTION = (270, 190)

PROFILE_PICTURE_RESOLUTION = (360, 360)

THUMBNAIL_PROFILE_PICTURE_RESOLUTION = (40, 40)

DEFAULT_IMAGE_PATH = r'F:\RetelShop\images\default_main_photo.png'

DEFAULT_THUMBNAIL_IMAGE_PATH = r'F:\RetelShop\images\default_thumbnail_main_photo.png'


LOGIN_URL = reverse_lazy('registration:login')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = socket.gethostbyname('smtp.gmail.com')

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = config('MY_EMAIL')

EMAIL_HOST_PASSWORD = config('APP_PASSWORD')

STRIPE_API_KEY = config('STRIPE_API_KEY')

MY_EMAIL = config('MY_EMAIL')

MONGODB_USERNAME = config('MONGODB_USERNAME')

MONGODB_PASSWORD = config('MONGODB_PASSWORD')


LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'products/home'


SOCIAL_AUTH_FACEBOOK_KEY = config('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = config('SOCIAL_AUTH_FACEBOOK_SECRET')

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
