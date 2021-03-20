from .common import *

# AWS Setting
USE_AWS = True
AWS_REGION = 'ap-northeast-2'
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = False
AWS_S3_HOST = 's3.%s.amazonaws.com' % AWS_REGION
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_DEFAULT_ACL = None

# Static Setting
STATIC_URL = "https://{}/static/".format(AWS_S3_CUSTOM_DOMAIN)
STATICFILES_STORAGE = 'buynsell.storages.StaticStorage'

# Media Setting
MEDIA_URL = "https://{}/media/".format(AWS_S3_CUSTOM_DOMAIN)
DEFAULT_FILE_STORAGE = 'buynsell.storages.MediaStorage'
