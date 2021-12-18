from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMatchProfilesAppConfig(AppConfig):
    default = True
    name = 'speedy.match.profiles'
    verbose_name = _("Speedy Match Profiles")
    label = 'match_profiles'


