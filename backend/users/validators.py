import re

from django.conf import settings
from django.core.exceptions import ValidationError

PATTERN = re.compile(r"^[\w.@+-]+$")


def validate_username(value):
    """Метод валидации никнейма."""
    if not PATTERN.match(value):
        raise ValidationError("В никнейме могут быть только буквы, цифры и @/./+/-/_.")
    if value in settings.NICKNAME_BLACKLIST:
        raise ValidationError(f'Нельзя использовать никнейм "{value}".')
    return value
