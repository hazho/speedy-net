import logging
import hashlib
import random
from datetime import timedelta, datetime, date
from haversine import haversine, Unit

from django.db.models import prefetch_related_objects
from django.utils.timezone import now
from django.utils.translation import get_language

from speedy.core.base.utils import get_age_ranges_match, string_is_not_empty
from speedy.core.base.managers import BaseManager
from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class SiteProfileManager(BaseManager):
    # Same function as user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile), but more optimized.
    def _get_rank(self, user, other_user, blocked_users_ids, blocking_users_ids):
        if (user.pk == other_user.pk):
            return self.model.RANK_0
        if (not (other_user.photo.visible_on_website)):
            return self.model.RANK_0
        if (other_user.gender not in user.speedy_match_profile.gender_to_match):
            return self.model.RANK_0
        if (user.gender not in other_user.speedy_match_profile.gender_to_match):
            return self.model.RANK_0
        if (not (user.speedy_match_profile.min_age_to_match <= other_user.get_age() <= user.speedy_match_profile.max_age_to_match)):
            return self.model.RANK_0
        if (not (other_user.speedy_match_profile.min_age_to_match <= user.get_age() <= other_user.speedy_match_profile.max_age_to_match)):
            return self.model.RANK_0
        if (not ((self.model.settings.MIN_HEIGHT_TO_MATCH <= user.speedy_match_profile.height <= self.model.settings.MAX_HEIGHT_TO_MATCH) and (self.model.settings.MIN_HEIGHT_TO_MATCH <= other_user.speedy_match_profile.height <= self.model.settings.MAX_HEIGHT_TO_MATCH))):
            return self.model.RANK_0
        if (user.speedy_match_profile.not_allowed_to_use_speedy_match or other_user.speedy_match_profile.not_allowed_to_use_speedy_match):
            return self.model.RANK_0
        if (other_user.pk in blocked_users_ids):
            return self.model.RANK_0
        if (other_user.pk in blocking_users_ids):
            return self.model.RANK_0
        other_diet_rank = other_user.speedy_match_profile.diet_match.get(str(user.diet), self.model.RANK_0)
        other_smoking_status_rank = other_user.speedy_match_profile.smoking_status_match.get(str(user.smoking_status), self.model.RANK_0)
        other_relationship_status_rank = other_user.speedy_match_profile.relationship_status_match.get(str(user.relationship_status), self.model.RANK_0)
        other_user_rank = min([other_diet_rank, other_smoking_status_rank, other_relationship_status_rank])
        if (other_user_rank == self.model.RANK_0):
            return self.model.RANK_0
        diet_rank = user.speedy_match_profile.diet_match.get(str(other_user.diet), self.model.RANK_0)
        smoking_status_rank = user.speedy_match_profile.smoking_status_match.get(str(other_user.smoking_status), self.model.RANK_0)
        relationship_status_rank = user.speedy_match_profile.relationship_status_match.get(str(other_user.relationship_status), self.model.RANK_0)
        rank = min([diet_rank, smoking_status_rank, relationship_status_rank])
        return rank

    def _ensure_cached_counts(self, other_user):
        if (other_user.speedy_match_profile.likes_to_user_count is None):
            other_user.speedy_match_profile.likes_to_user_count = len(other_user.likes_to_user.all())
            other_user.speedy_match_profile.save()
        if (other_user.speedy_net_profile.friends_count is None):
            other_user.speedy_net_profile.friends_count = len(other_user.friends.all())
            other_user.speedy_net_profile.save()

    def _prefetch_related_objects_if_no_cached_counts(self, user_list):
        users_to_prefetch = [user for user in user_list if ((user.speedy_match_profile.likes_to_user_count is None) or (user.speedy_net_profile.friends_count is None))]
        prefetch_related_objects(users_to_prefetch, 'likes_to_user', 'friends')

    def get_matches(self, user):
        """
        Get matches from database.

        Checks only first 2,400 users who match this user (sorted by last visit to Speedy Match), and return up to 720 users.
        """
        user.speedy_match_profile._set_values_to_match()
        age_ranges = get_age_ranges_match(min_age=user.speedy_match_profile.min_age_to_match, max_age=user.speedy_match_profile.max_age_to_match)
        language_code = get_language()
        logger.debug("SiteProfileManager::get_matches:start:user={user}, language_code={language_code}".format(
            user=user,
            language_code=language_code,
        ))
        datetime_now = datetime.now()
        timezone_now = now()
        today = date.today()
        # blocked_users_ids = Block.objects.filter(blocker__pk=user.pk).values_list('blocked_id', flat=True)
        # blocking_users_ids = Block.objects.filter(blocked__pk=user.pk).values_list('blocker_id', flat=True)
        blocked_users_ids = [block.blocked_id for block in user.blocked_entities.all()]
        blocking_users_ids = [block.blocker_id for block in user.blocking_entities.all()]
        qs = User.objects.active(
            photo__visible_on_website=True,
            gender__in=user.speedy_match_profile.gender_to_match,
            diet__in=user.speedy_match_profile.diet_to_match,
            smoking_status__in=user.speedy_match_profile.smoking_status_to_match,
            relationship_status__in=user.speedy_match_profile.relationship_status_to_match,
            speedy_match_site_profile__gender_to_match__contains=[user.gender],
            speedy_match_site_profile__diet_to_match__contains=[user.diet],
            speedy_match_site_profile__smoking_status_to_match__contains=[user.smoking_status],
            speedy_match_site_profile__relationship_status_to_match__contains=[user.relationship_status],
            date_of_birth__range=age_ranges,
            speedy_match_site_profile__min_age_to_match__lte=user.get_age(),
            speedy_match_site_profile__max_age_to_match__gte=user.get_age(),
            speedy_match_site_profile__height__range=(self.model.settings.MIN_HEIGHT_TO_MATCH, self.model.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
            speedy_match_site_profile__last_visit__gte=timezone_now - timedelta(days=720),
        ).exclude(
            pk__in=[user.pk] + blocked_users_ids + blocking_users_ids,
        ).order_by('-speedy_match_site_profile__last_visit')
        user_list = qs[:2400]
        self._prefetch_related_objects_if_no_cached_counts(user_list=user_list)
        # matches_list = [other_user for other_user in user_list if ((other_user.speedy_match_profile.is_active) and (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > self.model.RANK_0))]
        matches_list = []
        for other_user in user_list:
            other_user.speedy_match_profile.rank = self._get_rank(
                user=user,
                other_user=other_user,
                blocked_users_ids=blocked_users_ids,
                blocking_users_ids=blocking_users_ids,
            )
            if ((other_user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.rank > self.model.RANK_0)):
                self._ensure_cached_counts(other_user=other_user)
                other_user.speedy_match_profile._likes_to_user_count = other_user.speedy_match_profile.likes_to_user_count
                other_user.speedy_match_profile._friends_count = other_user.speedy_net_profile.friends_count
                other_user.speedy_match_profile._distance_between_users = None
                other_user.speedy_match_profile._user_last_visit_days_offset = 0 * 30
                if ((timezone_now - other_user.speedy_match_profile.last_visit).days >= 180):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 6 * 30
                if ((timezone_now - other_user.date_created).days < 15) or ((timezone_now - other_user.speedy_match_profile.last_visit).days < 5):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    if (other_user.speedy_match_profile.rank >= self.model.RANK_5) and ((timezone_now - other_user.speedy_match_profile.last_visit).days < 10):
                        other_user.speedy_match_profile._user_last_visit_days_offset += 0
                    else:
                        if (other_user.speedy_match_profile._likes_to_user_count >= 10):
                            other_user.speedy_match_profile._user_last_visit_days_offset += 0
                        elif (other_user.speedy_match_profile._likes_to_user_count >= 3):
                            other_user.speedy_match_profile._user_last_visit_days_offset += 30
                        else:
                            other_user.speedy_match_profile._user_last_visit_days_offset += 80
                    if (other_user.speedy_match_profile.rank >= self.model.RANK_5):
                        other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                    else:
                        if (other_user.speedy_match_profile._friends_count >= 20):
                            other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                        else:
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        if (other_user.get_age() >= 18):
                            if (120 <= other_user.speedy_match_profile.height <= 235):
                                other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                            else:
                                other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        else:
                            if (50 <= other_user.speedy_match_profile.height <= 235):
                                other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                            else:
                                other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                if ((timezone_now - other_user.speedy_match_profile.last_visit).days < 10):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    if (other_user.speedy_match_profile.rank >= self.model.RANK_5) and ((timezone_now - other_user.speedy_match_profile.last_visit).days < 20):
                        other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                    else:
                        # Generate a random number which changes every 4 hours, but doesn't change when reloading the page.
                        s = int(hashlib.md5("$$$-{}-{}-{}-{}-{}-$$$".format(other_user.id, today.isoformat(), (((datetime_now.hour // 4) + 1) * 97), (int(other_user.id) % 777), (int(other_user.id) % 458)).encode('utf-8')).hexdigest(), 16) % 12
                        if (5 <= s < 9):  # 4/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        elif (9 <= s < 12):  # 3/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 2 * 30
                        else:  # 5/12
                            other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                # Generate a random number which changes every 4 hours, but doesn't change when reloading the page.
                s = int(hashlib.md5("$$$-{}-{}-{}-{}-$$$".format(user.id, other_user.id, today.isoformat(), (((datetime_now.hour // 4) + 1) * 92)).encode('utf-8')).hexdigest(), 16) % 1000
                if (0 <= s < 120):  # 12/100
                    if (0 <= s < 12):
                        distance_offset = int((s % 3) * 2 / 10 * 6 * 30 + 0.5)
                    else:
                        distance_offset = int((s % 3 + 3) * 2 / 10 * 6 * 30 + 0.5)
                    if (random.randint(0, 399) == 0):
                        logger.debug("SiteProfileManager::get_matches:distance_offset #1: {user} and {other_user}, s is {s}, distance offset is {distance_offset} .".format(
                            user=user,
                            other_user=other_user,
                            s=s,
                            distance_offset=distance_offset,
                        ))
                else:
                    distance_offset = int(10 / 10 * 6 * 30 + 0.5)
                    try:
                        if ((user.last_ip_address_used_raw_ipapi_results is not None) and (other_user.last_ip_address_used_raw_ipapi_results is not None)):
                            user_latitude = user.last_ip_address_used_raw_ipapi_results["latitude"]
                            user_longitude = user.last_ip_address_used_raw_ipapi_results["longitude"]
                            other_user_latitude = other_user.last_ip_address_used_raw_ipapi_results["latitude"]
                            other_user_longitude = other_user.last_ip_address_used_raw_ipapi_results["longitude"]
                            distance_between_users = haversine(point1=(user_latitude, user_longitude), point2=(other_user_latitude, other_user_longitude), unit=Unit.KILOMETERS)
                            if (distance_between_users < 60):
                                distance_offset = int(0 / 10 * 6 * 30 + 0.5)
                            elif (distance_between_users < 300):
                                distance_offset = int(2 / 10 * 6 * 30 + 0.5)
                            elif (distance_between_users < 1200):
                                distance_offset = int(4 / 10 * 6 * 30 + 0.5)
                            elif (distance_between_users < 3000):
                                distance_offset = int(6 / 10 * 6 * 30 + 0.5)
                            elif (distance_between_users < 6000):
                                distance_offset = int(8 / 10 * 6 * 30 + 0.5)
                            else:
                                distance_offset = int(10 / 10 * 6 * 30 + 0.5)
                            other_user.speedy_match_profile._distance_between_users = distance_between_users
                            if (random.randint(0, 399) == 0):
                                logger.debug("SiteProfileManager::get_matches:distance_offset #2:s is {s}, distance offset is {distance_offset}, The distance between {user} and {other_user} is {distance_between_users} km.".format(
                                    user=user,
                                    other_user=other_user,
                                    distance_between_users=distance_between_users,
                                    s=s,
                                    distance_offset=distance_offset,
                                ))
                    except Exception as e:
                        logger.debug("SiteProfileManager::get_matches:Can't calculate distance between users, user={user}, other_user={other_user}, Exception={e} (registered {registered_days_ago} days ago)".format(
                            user=user,
                            other_user=other_user,
                            e=str(e),
                            registered_days_ago=(now() - user.date_created).days,
                        ))
                        distance_offset = int(10 / 10 * 6 * 30 + 0.5)
                other_user.speedy_match_profile._user_last_visit_days_offset += distance_offset
                if (other_user.speedy_match_profile.rank >= self.model.RANK_5):
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 1 * 30
                if (other_user.speedy_match_profile._user_last_visit_days_offset < 0):
                    other_user.speedy_match_profile._user_last_visit_days_offset = 0
                profile_description = other_user.speedy_match_profile.profile_description
                if (string_is_not_empty(profile_description)):
                    profile_description_split = profile_description.split()
                else:
                    profile_description_split = "".split()
                match_description = other_user.speedy_match_profile.match_description
                if (string_is_not_empty(match_description)):
                    match_description_split = match_description.split()
                else:
                    match_description_split = "".split()
                if ((string_is_not_empty(profile_description)) and (len(profile_description) >= 20) and (len(profile_description_split) >= 10)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 3 * 30
                if ((string_is_not_empty(match_description)) and (len(match_description) >= 20) and (len(match_description_split) >= 8)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                if ((string_is_not_empty(profile_description)) and (len(profile_description_split) > 0) and (len(profile_description_split) / len(set(profile_description_split)) < 2.5)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 20 * 30
                if ((string_is_not_empty(match_description)) and (len(match_description_split) > 0) and (len(match_description_split) / len(set(match_description_split)) < 2.5)):
                    other_user.speedy_match_profile._user_last_visit_days_offset += 0 * 30
                else:
                    other_user.speedy_match_profile._user_last_visit_days_offset += 20 * 30
                other_user.speedy_match_profile._user_last_visit_days_offset += other_user.speedy_match_profile.profile_picture_months_offset * 30
                # Generate a random number which changes every 4 hours, but doesn't change when reloading the page.
                s = int(hashlib.md5("$$$-{}-{}-{}-{}-{}-$$$".format(other_user.id, today.isoformat(), (((datetime_now.hour // 4) + 1) * 98), (int(other_user.id) % 777), (int(other_user.id) % 458)).encode('utf-8')).hexdigest(), 16) % 77
                if (74 <= s < 77):  # 3/77
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 6 * 30
                elif (71 <= s < 74):  # 3/77
                    other_user.speedy_match_profile._user_last_visit_days_offset -= 2 * 30
                else:  # 71/77
                    if ((timezone_now - other_user.speedy_match_profile.last_visit).days < 5):
                        other_user.speedy_match_profile._user_last_visit_days_offset -= 0 * 30
                    else:
                        if (48 <= s < 71):  # 23/77
                            other_user.speedy_match_profile._user_last_visit_days_offset += 1 * 30
                        elif (25 <= s < 48):  # 23/77
                            other_user.speedy_match_profile._user_last_visit_days_offset += 2 * 30
                        else:  # 25/77
                            other_user.speedy_match_profile._user_last_visit_days_offset -= 0 * 30
                matches_list.append(other_user)
        if (not (len(matches_list) == len(user_list))):
            # This is an error. All users should have ranks more than 0.
            logger.error('SiteProfileManager::get_matches:get inside "if (not (len(matches_list) == len(user_list))):", user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}'.format(
                user=user,
                language_code=language_code,
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
            ))
        matches_list = sorted(matches_list, key=lambda u: (-(max([((timezone_now - u.speedy_match_profile.last_visit).days + u.speedy_match_profile._user_last_visit_days_offset), 0]) // 40), u.speedy_match_profile.rank, u.speedy_match_profile.last_visit), reverse=True)
        matches_list = matches_list[:720]
        # Save number of matches in this language in user's profile.
        user.speedy_match_profile.number_of_matches = len(matches_list)
        user.speedy_match_profile.save()
        logger.debug("SiteProfileManager::get_matches:end:user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}, user_id_list={user_id_list}, distance_between_users_list={distance_between_users_list}".format(
            user=user,
            language_code=language_code,
            number_of_users=len(user_list),
            number_of_matches=len(matches_list),
            user_id_list=[u.id for u in matches_list[:40]],
            distance_between_users_list=[getattr(u.speedy_match_profile, "_distance_between_users", None) for u in matches_list[:40]],
        ))
        if ((not (self.model.settings.MIN_HEIGHT_TO_MATCH <= user.speedy_match_profile.height <= self.model.settings.MAX_HEIGHT_TO_MATCH)) or (user.speedy_match_profile.height <= 85) or (user.speedy_match_profile.not_allowed_to_use_speedy_match)):
            logger.warning("SiteProfileManager::get_matches:user={user}, language_code={language_code}, number_of_users={number_of_users}, number_of_matches={number_of_matches}, height={height}, not_allowed_to_use_speedy_match={not_allowed_to_use_speedy_match}".format(
                user=user,
                language_code=language_code,
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
                height=user.speedy_match_profile.height,
                not_allowed_to_use_speedy_match=user.speedy_match_profile.not_allowed_to_use_speedy_match,
            ))
        return matches_list

    def get_matches_from_list(self, user, from_list):
        user.speedy_match_profile._set_values_to_match()
        age_ranges = get_age_ranges_match(min_age=user.speedy_match_profile.min_age_to_match, max_age=user.speedy_match_profile.max_age_to_match)
        language_code = get_language()
        logger.debug("SiteProfileManager::get_matches_from_list:start:user={user}, language_code={language_code}".format(
            user=user,
            language_code=language_code,
        ))
        timezone_now = now()
        # blocked_users_ids = Block.objects.filter(blocker__pk=user.pk).values_list('blocked_id', flat=True)
        # blocking_users_ids = Block.objects.filter(blocked__pk=user.pk).values_list('blocker_id', flat=True)
        blocked_users_ids = [block.blocked_id for block in user.blocked_entities.all()]
        blocking_users_ids = [block.blocker_id for block in user.blocking_entities.all()]
        qs = User.objects.active(
            pk__in=from_list,
            photo__visible_on_website=True,
            gender__in=user.speedy_match_profile.gender_to_match,
            diet__in=user.speedy_match_profile.diet_to_match,
            smoking_status__in=user.speedy_match_profile.smoking_status_to_match,
            relationship_status__in=user.speedy_match_profile.relationship_status_to_match,
            speedy_match_site_profile__gender_to_match__contains=[user.gender],
            speedy_match_site_profile__diet_to_match__contains=[user.diet],
            speedy_match_site_profile__smoking_status_to_match__contains=[user.smoking_status],
            speedy_match_site_profile__relationship_status_to_match__contains=[user.relationship_status],
            date_of_birth__range=age_ranges,
            speedy_match_site_profile__min_age_to_match__lte=user.get_age(),
            speedy_match_site_profile__max_age_to_match__gte=user.get_age(),
            speedy_match_site_profile__height__range=(self.model.settings.MIN_HEIGHT_TO_MATCH, self.model.settings.MAX_HEIGHT_TO_MATCH),
            speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
            speedy_match_site_profile__active_languages__contains=[language_code],
        ).exclude(
            pk__in=[user.pk] + blocked_users_ids + blocking_users_ids,
        ).order_by('-speedy_match_site_profile__last_visit')
        user_list = qs
        # matches_list = [other_user for other_user in user_list if ((other_user.speedy_match_profile.is_active) and (user.speedy_match_profile.get_matching_rank(other_profile=other_user.speedy_match_profile) > self.model.RANK_0))]
        matches_list = []
        for other_user in user_list:
            other_user.speedy_match_profile.rank = self._get_rank(
                user=user,
                other_user=other_user,
                blocked_users_ids=blocked_users_ids,
                blocking_users_ids=blocking_users_ids,
            )
            if ((other_user.speedy_match_profile.is_active) and (other_user.speedy_match_profile.rank > self.model.RANK_0)):
                matches_list.append(other_user)
        if (not (len(matches_list) == len(user_list))):
            # This is an error. All users should have ranks more than 0.
            logger.error('SiteProfileManager::get_matches_from_list:get inside "if (not (len(matches_list) == len(user_list))):", user={user}, language_code={language_code}, from_list_len={from_list_len}, number_of_users={number_of_users}, number_of_matches={number_of_matches}'.format(
                user=user,
                language_code=language_code,
                from_list_len=len(from_list),
                number_of_users=len(user_list),
                number_of_matches=len(matches_list),
            ))
        matches_list = sorted(matches_list, key=lambda u: (-((timezone_now - u.speedy_match_profile.last_visit).days // 40), u.speedy_match_profile.rank, u.speedy_match_profile.last_visit), reverse=True)
        logger.debug("SiteProfileManager::get_matches_from_list:end:user={user}, language_code={language_code}, from_list_len={from_list_len}, number_of_users={number_of_users}, number_of_matches={number_of_matches}".format(
            user=user,
            language_code=language_code,
            from_list_len=len(from_list),
            number_of_users=len(user_list),
            number_of_matches=len(matches_list),
        ))
        return matches_list


