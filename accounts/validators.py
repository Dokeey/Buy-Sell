from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from .models import Profile


def id_validate(value):
    user = Profile.objects.filter(nick_name=value)
    if user:
        raise ValidationError(
            _("'{}' is already exists.".format(value)),
        )
    return None
