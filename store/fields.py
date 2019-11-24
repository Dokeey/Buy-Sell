import os
from random import randrange

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from imagekit.models import ProcessedImageField
from imagekit.models.fields import ProcessedImageFieldFile


def get_random():
    rand = randrange(1,10)
    return 'profile/{}.png'.format(rand)

# DEFAULT_IMAGE_PATH = get_random()


class DefaultStaticImageFieldFile(ProcessedImageFieldFile):
    @property
    def url(self):
        try:
            # 파일이 존재한다면  부모의 url속성을 리턴합니다.
            return super().url
        except ValueError:
            # 파일이 없다면 ValueError가 발생합니다.
            from django.contrib.staticfiles.storage import staticfiles_storage
            from django.contrib.staticfiles import finders

            img_path = get_random()
            # self.static_image_path = img_path
            if os.environ.get('DJANGO_SETTINGS_MODULE') == 'buynsell.settings.dev':
                url = finders.find(img_path)
                self.save(
                    "default_image",
                    File(open(url, 'rb'))
                )
            else:
                url = staticfiles_storage.url(img_path)
                res = requests.get(url, stream=True)
                self.save("default_image", ContentFile(res.content))

            # if not self.DEFAULT_IMAGE_PATH:
            #     self.DEFAULT_IMAGE_PATH = get_random()
            return self.storage.url(self.name)

class DefaultStaticProcessedImageField(ProcessedImageField):
    # field에 접근 시 프록시로 사용할 필드파일 클래스를 지정합니다.
    attr_class = DefaultStaticImageFieldFile
    # static_image_path = ''
