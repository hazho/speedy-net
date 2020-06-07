from django.conf import settings as django_settings
from django.core import mail

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_speedy_match
    from speedy.core.accounts.models import User
    from speedy.core.blocks.models import Block
    from speedy.match.likes.models import UserLike

    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    @only_on_speedy_match
    class LikeBlocksTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory())
            UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory())
            UserLike.objects.add_like(from_user=self.user_2, to_user=ActiveUserFactory())
            UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user_1)
            UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user_2)
            UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user_2)

        def assert_counters(self, user, from_user_likes, to_user_likes):
            self.assertEqual(first=len(UserLike.objects.filter(from_user=user)), second=from_user_likes)
            self.assertEqual(first=len(UserLike.objects.filter(to_user=user)), second=to_user_likes)

        def test_set_up(self):
            self.assert_counters(user=self.user_1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=2)

        def test_if_no_relation_between_users_nothing_get_affected(self):
            Block.objects.block(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=2)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=2)

        def test_if_user1_blocked_user2_like_is_removed(self):
            UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
            self.assert_counters(user=self.user_1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=3)
            Block.objects.block(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=2)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
            self.assert_counters(user=self.user_1, from_user_likes=2, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=2)

        def test_if_user2_blocked_user1_like_isnt_removed(self):
            UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
            self.assert_counters(user=self.user_1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=3)
            Block.objects.block(blocker=self.user_2, blocked=self.user_1)
            self.assert_counters(user=self.user_1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=3)
            Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
            self.assert_counters(user=self.user_1, from_user_likes=3, to_user_likes=1)
            self.assert_counters(user=self.user_2, from_user_likes=1, to_user_likes=3)


    @only_on_speedy_match
    class LikeNotificationsTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()

        def test_user_gets_notified_on_like(self):
            self.assertEqual(first=len(mail.outbox), second=0)
            self.assertEqual(first=self.user_1.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
            self.assertEqual(first=self.user_2.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
            UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
            self.assertEqual(first=len(mail.outbox), second=1)
            self.assertEqual(first=mail.outbox[0].subject, second='Someone likes you on @@ {}'.format(self.site_name))

        def test_user_doesnt_get_notified_on_like(self):
            self.assertEqual(first=len(mail.outbox), second=0)
            self.user_1.speedy_match_profile.notify_on_like = User.NOTIFICATIONS_OFF
            self.user_1.save_user_and_profile()
            self.assertEqual(first=self.user_1.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_OFF)
            self.assertEqual(first=self.user_2.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
            UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
            self.assertEqual(first=len(mail.outbox), second=0)


