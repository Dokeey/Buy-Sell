from django.core.exceptions import ValidationError

from .models import Profile


def id_validate(value):
    user = Profile.objects.filter(nick_name=value)
    if user:
        raise ValidationError(
            _("'{}' is already exists.".format(value)),
        )
    return None
