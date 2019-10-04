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
            from django.contrib.staticfiles import finders
            # staticfiles app의 finders를 사용해 FieldFile에 연결된 field의
            # static_image_path값에 해당하는 파일이 있는지 검사합니다.
            # if finders.find(self.field.static_image_path):
            #     # 존재할경우 staticfiles_storage의 url메서드를 사용해
            #     # 정적파일에 액세스 할 수 있는 URL을 반환합니다.
            #     return staticfiles_storage.url(self.field.static_image_path)
            # static_image_path값에 해당하는 경로에 파일이 없다면
            # DEFAULT_IMAGE_PATH 경로의 파일을 사용합니다.

            img_path = get_random()
            res = requests.get(staticfiles_storage.url(img_path), stream=True)
            self.save(self.field.name, ContentFile(res.content))
            # if not self.DEFAULT_IMAGE_PATH:
            #     self.DEFAULT_IMAGE_PATH = get_random()
            return staticfiles_storage.url(img_path)

class DefaultStaticProcessedImageField(ProcessedImageField):
    # field에 접근 시 프록시로 사용할 필드파일 클래스를 지정합니다.
    attr_class = DefaultStaticImageFieldFile

    # def __init__(self, *args, **kwargs):
    #     # 필드의 속성중 'default_image_path'키로 주어진 값을 가져와 인스턴스의 static_image_path값으로 할당합니다.
    #     # 이 때, 속성이 지정되어 있지 않으면 settings모듈의 'DEFAULT_IMAGE_PATH'속성의 값을 가져오며,
    #     # 이것도 정의되어 있지 않다면 현재 모듈의 'DEFAULT_IMAGE_PATH'상수의 값을 사용합니다.
    #     self.static_image_path = kwargs.pop(
    #         'default_image_path',
    #         getattr(settings, 'DEFAULT_IMAGE_PATH', get_random()))
    #     # 추가 정의된 키워드인수의 값을 pop()으로 제거한 뒤, 부모의 초기화 메서드를 실행합니다.
    #     super().__init__(*args, **kwargs)