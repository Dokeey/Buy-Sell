from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class StaticAzureStorage(AzureStorage):
    azure_container = 'static'

    def url(self, name):
        if not settings.DEBUG:
            cdn_host = getattr(settings, 'CDN_HOST', None)
            if cdn_host:
                return "{}/{}/{}".format(cdn_host, self.azure_container, name)
        return super().url(name)


class MediaAzureStorage(AzureStorage):
    azure_container = 'media'