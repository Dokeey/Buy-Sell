from .common import *


# AWS Setting
AWS_REGION = 'ap-northeast-2'
AWS_STORAGE_BUCKET_NAME = 'elasticbeanstalk-ap-northeast-2-109247251546'
AWS_QUERYSTRING_AUTH = False
AWS_S3_HOST = 's3.%s.amazonaws.com' % AWS_REGION
AWS_ACCESS_KEY_ID = 'AKIARS35EYRNCE5R7HWL'
AWS_SECRET_ACCESS_KEY = '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'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# Static Setting
# STATIC_URL = "https://{}/static/".format(AWS_S3_CUSTOM_DOMAIN)
STATICFILES_STORAGE = 'buynsell.storages.StaticStorage'

# Media Setting
MEDIA_URL = "https://{}/media/".format(AWS_S3_CUSTOM_DOMAIN)
DEFAULT_FILE_STORAGE = 'buynsell.storages.MediaStorage'