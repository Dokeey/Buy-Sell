from .common import *


STATICFILES_STORAGE = 'buynsell.storages.StaticAzureStorage'
DEFAULT_FILE_STORAGE = 'buynsell.storages.MediaAzureStorage'

AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')
