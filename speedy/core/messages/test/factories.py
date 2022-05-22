from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import factory

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.messages.models import Chat


        class ChatFactory(factory.django.DjangoModelFactory):
            ent1 = factory.SubFactory(ActiveUserFactory)
            ent2 = factory.SubFactory(ActiveUserFactory)

            class Meta:
                model = Chat

            @factory.post_generation
            def group(self: Chat, created, extracted, **kwargs):
                if (extracted is not None):
                    assert self.is_group
                    for entity in extracted:
                        self.group.add(entity)


