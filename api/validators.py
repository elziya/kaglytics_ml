import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EnglishLettersValidator(object):
    def validate(self, password, user=None):
        if not re.findall('^[A-Za-z0-9]*$', password):
            raise ValidationError(
                _("Password may only contain latin characters and numbers."),
                code='password_no_english',
            )

    def get_help_text(self):
        return _(
            "Password may only contain latin characters and numbers."
        )
