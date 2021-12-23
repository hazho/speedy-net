from django.db.models import Q
from django.conf import settings as django_settings

from rules import predicate, add_perm, always_allow, always_deny

from speedy.core.accounts.base_rules import is_self, is_active
from speedy.core.accounts.rules import has_access_perm
from speedy.core.blocks.rules import is_blocked, there_is_block
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from speedy.core.messages.models import Chat
from speedy.core.blocks.models import Block
from speedy.match.likes.models import UserLike


@predicate
def is_match_profile(user, other_user):
    if (user.is_authenticated):
        if ((user.is_staff) and (user.is_superuser)):
            return True
        match_profile = (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > SpeedyMatchSiteProfile.RANK_0)
        has_message = Chat.objects.filter((Q(ent1_id=user) & Q(ent2_id=other_user)) | (Q(ent1_id=other_user) & Q(ent2_id=user))).exists()
        has_likes = UserLike.objects.filter((Q(from_user=user) & Q(to_user=other_user)) | (Q(from_user=other_user) & Q(to_user=user))).exists()
        has_blocked = Block.objects.has_blocked(blocker=user, blocked=other_user)
        return (is_self(user=user, other_user=other_user)) or ((is_active(user=user, other_user=other_user)) and (match_profile or has_message or has_likes or has_blocked))
    return False


if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
    add_perm('accounts.view_profile', has_access_perm & ~there_is_block & is_match_profile)
    add_perm('accounts.view_profile_header', has_access_perm & ~is_blocked & is_match_profile)
    add_perm('accounts.view_profile_info', has_access_perm & ~is_blocked & is_match_profile)
    add_perm('accounts.view_profile_age', always_allow)
    add_perm('accounts.view_profile_rank', has_access_perm & ~there_is_block & is_match_profile & ~is_self)
    add_perm('accounts.view_user_on_speedy_net_widget', has_access_perm & ~there_is_block & is_match_profile)
    add_perm('accounts.view_user_on_speedy_match_widget', always_deny)


