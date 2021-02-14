from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class SpeedyMatchMatchesAppConfig(AppConfig):
    name = 'speedy.match.matches'
    verbose_name = _("Speedy Match Matches")
    label = 'matches'


