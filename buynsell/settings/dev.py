from .common import *

# Application definition
INSTALLED_APPS = INSTALLED_APPS + [
    'debug_toolbar',

]

MIDDLEWARE = MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']


# Static
STATIC_URL = '/static/'

# Media
MEDIA_URL = '/media/' # 업로드 할 경로
