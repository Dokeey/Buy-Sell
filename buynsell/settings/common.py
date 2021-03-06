"""
Django settings for buynsell project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import socket

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_ve!tya9hxp$#n$md(#@11o_x%de8dagvbm9j$+5z)$%&l%utx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.humanize',

    'hitcount',  # 조회수

    'accounts.apps.AccountsConfig',
    'category.apps.CategoryConfig',
    'store.apps.StoreConfig',
    'trade.apps.TradeConfig',
    'mypage.apps.MypageConfig',
    'customer.apps.CustomerConfig',
    'policy.apps.PolicyConfig',

    'imagekit', # image
    'mptt', # category
    'django_extensions', # models relation graph
    'django_cleanup', # django delete media file
    # 'sslserver', # django SSL server module
    'django_summernote',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'accounts.middleware.KickMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.KickedMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'buynsell.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'buynsell', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'buynsell.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        # Database 엔진으로 postgresql을 사용
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

# USE_TZ = True
USE_TZ = False




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTH_USER_MODEL = 'accounts.User'

from django.urls import reverse_lazy

LOGIN_URL = reverse_lazy('accounts:login')
LOGIN_REDIRECT_URL = reverse_lazy('root')
LOGOUT_REDIRECT_URL = reverse_lazy('accounts:login')

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL')
DEFAULT_FROM_MAIL = 'BuynSell'


from django.utils.translation import ugettext_lazy as _

LANGUAGES = [  # Available languages
    ('en', _("English")),
    ('ko_kr', _("한국어")),
]


# IAMPORT API
IAMPORT_SHOP_ID = 'iamport' # 가맹점 식별코드
IAMPORT_API_KEY = 'imp_apikey' # REST API 키
IAMPORT_API_SECRET = 'ekKoeW8RyKuT0zgaZsUtXXTLQ4AhPFW3ZGseDA6bkA5lamv9OqDMnxyeB9wqOsuO9W3Mx9YSJ4dTqJ3f' # REST API SECRET

# Hit Count
HITCOUNT_KEEP_HIT_ACTIVE = { 'days': 1 }
HITCOUNT_KEEP_HIT_IN_DATABASE = { 'days': 30 }


# Message custom
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Model graph
GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}

# Session Time Out
SESSION_COOKIE_AGE = 3600   # 1시간
SESSION_SAVE_EVERY_REQUEST = True   # 리퀘스트시 세션 정보 갱신 허용

# KAKAO TALK API
KAKAO_KEY_JS = os.environ.get('KAKAO_KEY_JS')

# FACEBOOK API
FACEBOOK_KEY = os.environ.get('FACEBOOK_KEY')

# Django SSL 통신 관련 설정
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# summernote conf
SUMMERNOTE_CONFIG  = {
'summernote': {

        # Change editor size
        'width': '100%',
        'height': '480',
       ' lang ' : 'ko-KR',
}
}

USE_AWS = False
