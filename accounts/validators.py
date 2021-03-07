from django.core.validators import RegexValidator

phone_validate = RegexValidator(
    regex=r'^0\d{8,10}$',
    message='정확한 연락처를 적어주세요.',
    code='invalid_phone'
)
