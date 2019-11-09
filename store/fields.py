from random import randrange

import requests
from django.conf import settings
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
            img_path = get_random()
            if not self.field.static_image_path:
                self.field.static_image_path = img_path
                res = requests.get(staticfiles_storage.url(img_path), stream=True)
                self.save("default_image", ContentFile(res.content))
            # if not self.DEFAULT_IMAGE_PATH:
            #     self.DEFAULT_IMAGE_PATH = get_random()
            return staticfiles_storage.url(img_path)

class DefaultStaticProcessedImageField(ProcessedImageField):
    # field에 접근 시 프록시로 사용할 필드파일 클래스를 지정합니다.
    attr_class = DefaultStaticImageFieldFile
    static_image_path = ''

    # def __init__(self, *args, **kwargs):
    #     # 필드의 속성중 'default_image_path'키로 주어진 값을 가져와 인스턴스의 static_image_path값으로 할당합니다.
    #     # 이 때, 속성이 지정되어 있지 않으면 settings모듈의 'DEFAULT_IMAGE_PATH'속성의 값을 가져오며,
    #     # 이것도 정의되어 있지 않다면 현재 모듈의 'DEFAULT_IMAGE_PATH'상수의 값을 사용합니다.
    #     self.static_image_path = kwargs.pop(
    #         'default_image_path',
    #         getattr(settings, 'DEFAULT_IMAGE_PATH', get_random()))
    #     # 추가 정의된 키워드인수의 값을 pop()으로 제거한 뒤, 부모의 초기화 메서드를 실행합니다.
    #     super().__init__(*args, **kwargs)