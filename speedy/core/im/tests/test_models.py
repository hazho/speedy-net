from django.conf import settings
from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from speedy.core.settings.utils import env
from .test_factories import ChatFactory


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class ChatTestCase(TestCase):
    def test_id_length(self):
        chat = ChatFactory()
        self.assertEqual(first=len(chat.id), second=20)

    def test_str(self):
        chat = ChatFactory(ent1=ActiveUserFactory(first_name='Walter', last_name='White'), ent2=ActiveUserFactory(first_name='Jesse', last_name='Pinkman'))
        if (int(settings.SITE_ID) == int(env('SPEEDY_MATCH_SITE_ID'))):
            self.assertEqual(first=str(chat), second='Walter, Jesse')
        else:
            self.assertEqual(first=str(chat), second='Walter White, Jesse Pinkman')

    def test_get_slug(self):
        user1=ActiveUserFactory(first_name='Walter', last_name='White', slug='walter')
        user2=ActiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse')
        chat = ChatFactory(ent1=user1, ent2=user2)
        self.assertEqual(first=chat.get_slug(current_user=user1), second='jesse')
        self.assertEqual(first=chat.get_slug(current_user=user2), second='walter')
        chat = ChatFactory(ent1=None, ent2=None, is_group=True, group=[user1, user2, ActiveUserFactory(), ActiveUserFactory()])
        self.assertEqual(first=chat.get_slug(current_user=user1), second=chat.id)
