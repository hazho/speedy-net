from django.conf import settings as django_settings

if (django_settings.TESTS):
    from django.db import connection

    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin

    from speedy.core.base.utils import to_attribute
    from speedy.core.accounts.models import Entity, User, UserEmailAddress


    class SpeedyCoreAccountsModelsMixin(object):
        def assert_models_count(self, entity_count, user_count, user_email_address_count, confirmed_email_address_count, unconfirmed_email_address_count):
            self.assertEqual(first=Entity.objects.count(), second=entity_count)
            self.assertEqual(first=User.objects.count(), second=user_count)
            self.assertEqual(first=UserEmailAddress.objects.count(), second=user_email_address_count)
            self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=True).count(), second=confirmed_email_address_count)
            self.assertEqual(first=UserEmailAddress.objects.filter(is_confirmed=False).count(), second=unconfirmed_email_address_count)

        def assert_user_email_addresses_count(self, user, user_email_addresses_count, user_primary_email_addresses_count, user_confirmed_email_addresses_count, user_unconfirmed_email_addresses_count):
            self.assertEqual(first=user.email_addresses.count(), second=user_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_primary=True).count(), second=user_primary_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_confirmed=True).count(), second=user_confirmed_email_addresses_count)
            self.assertEqual(first=user.email_addresses.filter(is_confirmed=False).count(), second=user_unconfirmed_email_addresses_count)
            if (user_confirmed_email_addresses_count > 0):
                self.assertEqual(first=user.has_confirmed_email, second=True)
                self.assertEqual(first=user.email_addresses.filter(is_confirmed=True, is_primary=True).count(), second=user_primary_email_addresses_count)
            else:
                self.assertEqual(first=user.has_confirmed_email, second=False)
                self.assertEqual(first=user.email_addresses.filter(is_confirmed=True, is_primary=True).count(), second=0)

        def assert_user_first_and_last_name_in_all_languages(self, user):
            self.assertTupleEqual(tuple1=User.NAME_LOCALIZABLE_FIELDS, tuple2=('first_name', 'last_name'))
            self.assertEqual(first=user.first_name_en, second=user.first_name)
            self.assertEqual(first=user.first_name_he, second=user.first_name)
            self.assertEqual(first=user.last_name_en, second=user.last_name)
            self.assertEqual(first=user.last_name_he, second=user.last_name)
            field_name_localized_list = list()
            for base_field_name in User.NAME_LOCALIZABLE_FIELDS:
                for language_code, language_name in django_settings.LANGUAGES:
                    field_name_localized = to_attribute(name=base_field_name, language_code=language_code)
                    self.assertEqual(first=getattr(user, field_name_localized), second=getattr(user, base_field_name), msg="assert_user_first_and_last_name_in_all_languages::fields don't match ({field_name_localized}, {base_field_name}), user.pk={user_pk}, user.username={user_username}, user.slug={user_slug}, user.name={user_name}".format(
                        field_name_localized=field_name_localized,
                        base_field_name=base_field_name,
                        user_pk=user.pk,
                        user_username=user.username,
                        user_slug=user.slug,
                        user_name=user.name,
                    ))
                    field_name_localized_list.append(field_name_localized)
            self.assertListEqual(list1=field_name_localized_list, list2=['first_name_en', 'first_name_he', 'last_name_en', 'last_name_he'])


    class SpeedyCoreAccountsLanguageMixin(SpeedyCoreBaseLanguageMixin):
        _first_password_field_names = ['new_password1']
        _both_password_field_names = ['new_password1', 'new_password2']

        def _assert_model_is_entity_or_user(self, model):
            self.assertIn(member=model, container=[Entity, User])
            if (model is Entity):
                pass
            elif (model is User):
                pass
            else:
                raise Exception("Unexpected: model={}".format(model))

        def _value_is_not_a_valid_choice_error_message_by_value(self, value):
            return self._value_is_not_a_valid_choice_error_message_to_format.format(value=value)

        def _value_must_be_an_integer_error_message_by_value(self, value):
            return self._value_must_be_an_integer_error_message_to_format.format(value=value)

        def _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
            return self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format.format(min_length=min_length, value_length=value_length)

        def _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            return self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

        def _username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(self, min_length, value_length):
            return self._username_must_contain_at_least_min_length_characters_error_message_to_format.format(min_length=min_length, value_length=value_length)

        def _username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(self, max_length, value_length):
            return self._username_must_contain_at_most_max_length_characters_error_message_to_format.format(max_length=max_length, value_length=value_length)

        def _a_confirmation_message_was_sent_to_email_address_error_message_by_email_address(self, email_address):
            return self._a_confirmation_message_was_sent_to_email_address_error_message_to_format.format(email_address=email_address)

        def _user_all_the_required_fields_keys(self):
            return [field_name.format(language_code=language_code) for field_name in ['first_name_{language_code}'] for language_code, language_name in django_settings.LANGUAGES] + ['username', 'slug', 'password', 'gender', 'date_of_birth']

        def _registration_form_all_the_required_fields_keys(self):
            return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'email', 'slug', 'new_password1', 'gender', 'date_of_birth']]

        def _profile_form_all_the_required_fields_keys(self):
            return [field_name.format(language_code=self.language_code) for field_name in ['first_name_{language_code}', 'slug', 'gender', 'date_of_birth']]

        def _registration_form_all_the_required_fields_are_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._registration_form_all_the_required_fields_keys())

        def _profile_form_all_the_required_fields_are_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._profile_form_all_the_required_fields_keys())

        def _date_of_birth_is_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=['date_of_birth'])

        def _enter_a_valid_date_errors_dict(self):
            return {'date_of_birth': [self._enter_a_valid_date_error_message]}

        def _cannot_create_user_email_address_without_all_the_required_fields_errors_dict(self):
            return {
                'user': [self._this_field_cannot_be_null_error_message],
                'email': [self._this_field_cannot_be_blank_error_message],
            }

        def _id_contains_illegal_characters_errors_dict(self):
            return {'id': [self._id_contains_illegal_characters_error_message]}

        def _please_enter_a_correct_username_and_password_errors_dict(self):
            return {'__all__': [self._please_enter_a_correct_username_and_password_error_message]}

        def _invalid_password_errors_dict(self):
            return {'password': [self._invalid_password_error_message]}

        def _password_too_short_errors_dict(self, field_names):
            return {field_name: [self._password_too_short_error_message] for field_name in field_names}

        def _password_too_long_errors_dict(self, field_names):
            return {field_name: [self._password_too_long_error_message] for field_name in field_names}

        def _your_old_password_was_entered_incorrectly_errors_dict(self):
            return {'old_password': [self._your_old_password_was_entered_incorrectly_error_message]}

        def _the_two_password_fields_didnt_match_errors_dict(self):
            return {'new_password2': [self._the_two_password_fields_didnt_match_error_message]}

        def _enter_a_valid_email_address_errors_dict(self):
            return {'email': [self._enter_a_valid_email_address_error_message]}

        def _this_email_is_already_in_use_errors_dict(self):
            return {'email': [self._this_email_is_already_in_use_error_message]}

        def _this_username_is_already_taken_errors_dict(self, slug_fail=False, username_fail=False):
            self.assertIs(expr1=slug_fail, expr2=True)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._this_username_is_already_taken_error_message]
            if (username_fail):
                errors_dict['username'] = [self._this_username_is_already_taken_error_message]
            return errors_dict

        def _username_must_start_with_4_or_more_letters_errors_dict(self, model, slug_fail=False, username_fail=False):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                if (model is Entity):
                    errors_dict['slug'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['slug'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
            if (username_fail):
                if (model is Entity):
                    errors_dict['username'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['username'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
            return errors_dict

        def _slug_does_not_parse_to_username_errors_dict(self, model, username_fail=False):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {'slug': [self._slug_does_not_parse_to_username_error_message]}
            if (username_fail):
                if (model is Entity):
                    errors_dict['username'] = [self._entity_username_must_start_with_4_or_more_letters_error_message]
                elif (model is User):
                    errors_dict['username'] = [self._user_username_must_start_with_4_or_more_letters_error_message]
            return errors_dict

        def _date_of_birth_errors_dict_by_date_of_birth(self, date_of_birth):
            if (date_of_birth == ''):
                return self._date_of_birth_is_required_errors_dict()
            else:
                return self._enter_a_valid_date_errors_dict()

        def _you_cant_change_your_username_errors_dict_by_gender(self, gender):
            return {'slug': [self._you_cant_change_your_username_error_message_dict_by_gender[gender]]}

        def _cannot_create_user_without_all_the_required_fields_errors_dict_by_value(self, value, gender_is_valid=False):
            self.assertEqual(first=gender_is_valid, second=(value in User.GENDER_VALID_VALUES))
            if (value is None):
                str_value = ''
                gender_error_messages = [self._this_field_cannot_be_null_error_message]
            else:
                str_value = str(value)
                if (value == ''):
                    gender_error_messages = [self._value_must_be_an_integer_error_message_by_value(value=value)]
                else:
                    if (not (gender_is_valid)):
                        gender_error_messages = [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]
                    else:
                        gender_error_messages = None
            slug_and_username_error_messages = [self._user_username_must_start_with_4_or_more_letters_error_message]
            date_of_birth_error_messages = [self._enter_a_valid_date_error_message]
            errors_dict = {
                'username': slug_and_username_error_messages,
                'slug': slug_and_username_error_messages,
                'date_of_birth': date_of_birth_error_messages,
            }
            if (value in [None, '']):
                self.assertEqual(first=str_value, second='')
                for language_code, language_name in django_settings.LANGUAGES:
                    if (value is None):
                        errors_dict['first_name_{language_code}'.format(language_code=language_code)] = [self._this_field_cannot_be_null_error_message]
                        # ~~~~ TODO: last name ValidationError(_('This field cannot be null.')) is not raised when User() is created without a last name - should be raised!
                        # errors_dict['last_name_{language_code}'.format(language_code=language_code)] = [self._this_field_cannot_be_null_error_message]
                    elif (value == ''):
                        errors_dict['first_name_{language_code}'.format(language_code=language_code)] = [self._this_field_cannot_be_blank_error_message]
                    else:
                        raise NotImplementedError()
                errors_dict['password'] = [self._this_field_cannot_be_blank_error_message]
            else:
                self.assertNotEqual(first=str_value, second='')
            self.assertEqual(first=gender_is_valid, second=(gender_error_messages is None))
            if (not (gender_is_valid)):
                errors_dict['gender'] = gender_error_messages
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_least_min_length_alphanumeric_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_most_max_length_alphanumeric_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_least_min_length_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, slug_value_length=None, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_SLUG_LENGTH, value_length=slug_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_least_min_length_characters_error_message_by_min_length_and_value_length(min_length=model.settings.MIN_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _model_slug_or_username_username_must_contain_at_most_max_length_characters_errors_dict_by_value_length(self, model, slug_fail=False, username_fail=False, slug_value_length=None, username_value_length=None):
            self._assert_model_is_entity_or_user(model=model)
            errors_dict = {}
            if (slug_fail):
                errors_dict['slug'] = [self._username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_SLUG_LENGTH, value_length=slug_value_length)]
            if (username_fail):
                errors_dict['username'] = [self._username_must_contain_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=model.settings.MAX_USERNAME_LENGTH, value_length=username_value_length)]
            return errors_dict

        def _this_field_cannot_be_null_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._this_field_cannot_be_null_error_message]}

        def _this_field_cannot_be_blank_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._this_field_cannot_be_blank_error_message]}

        def _value_must_be_valid_json_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._value_must_be_valid_json_error_message]}

        def _ensure_this_value_is_greater_than_or_equal_to_minus_32768_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message]}

        def _ensure_this_value_is_less_than_or_equal_to_32767_errors_dict_by_field_name(self, field_name):
            return {field_name: [self._ensure_this_value_is_less_than_or_equal_to_32767_error_message]}

        def _value_is_not_a_valid_choice_errors_dict_by_field_name_and_value(self, field_name, value):
            return {field_name: [self._value_is_not_a_valid_choice_error_message_by_value(value=value)]}

        def _value_must_be_an_integer_errors_dict_by_field_name_and_value(self, field_name, value):
            return {field_name: [self._value_must_be_an_integer_error_message_by_value(value=value)]}

        def _this_field_cannot_be_null_errors_dict_by_field_name_list(self, field_name_list):
            return {field_name_list[i]: [self._this_field_cannot_be_null_error_message] for i in range(len(field_name_list))}

        def _value_must_be_an_integer_errors_dict_by_field_name_list_and_value_list(self, field_name_list, value_list):
            return {field_name_list[i]: [self._value_must_be_an_integer_error_message_by_value(value=value_list[i])] for i in range(len(field_name_list))}

        def _ensure_this_value_has_at_most_max_length_characters_errors_dict_by_field_name_and_max_length_and_value_length(self, field_name, max_length, value_length):
            return {field_name: [self._ensure_this_value_has_at_most_max_length_characters_error_message_by_max_length_and_value_length(max_length=max_length, value_length=value_length)]}

        def _not_null_constraint_error_message_by_column_and_relation(self, column, relation):
            postgresql_version = connection.cursor().connection.server_version
            if (postgresql_version < 130000):
                # msg = 'null value in column "{}" violates not-null constraint'
                raise NotImplementedError("postgresql version must be at least 13.0.")
            else:
                msg = 'null value in column "{}" of relation "{}" violates not-null constraint'
            return msg.format(column, relation)

        def set_up(self):
            super().set_up()

            _this_field_cannot_be_null_error_message_dict = {'en': 'This field cannot be null.', 'he': 'שדה זה אינו יכול להיות ריק.'}
            _this_field_cannot_be_blank_error_message_dict = {'en': 'This field cannot be blank.', 'he': 'שדה זה אינו יכול להיות ריק.'}
            _id_contains_illegal_characters_error_message_dict = {'en': 'id contains illegal characters.', 'he': 'id מכיל תווים לא חוקיים.'}
            _value_must_be_valid_json_error_message_dict = {'en': 'Value must be valid JSON.', 'he': 'ערך חייב להיות JSON חוקי.'}
            _invalid_password_error_message_dict = {'en': 'Invalid password.', 'he': 'הסיסמה לא תקינה.'}
            _password_too_short_error_message_dict = {'en': 'This password is too short. It must contain at least 8 characters.', 'he': 'סיסמה זו קצרה מדי. היא חייבת להכיל לפחות 8 תווים.'}
            _password_too_long_error_message_dict = {'en': 'This password is too long. It must contain at most 120 characters.', 'he': 'סיסמה זו ארוכה מדי. היא יכולה להכיל 120 תווים לכל היותר.'}
            _this_username_is_already_taken_error_message_dict = {'en': 'This username is already taken.', 'he': 'שם המשתמש/ת הזה כבר תפוס.'}
            _enter_a_valid_email_address_error_message_dict = {'en': 'Enter a valid email address.', 'he': 'נא להזין כתובת דואר אלקטרוני חוקית.'}
            _this_email_is_already_in_use_error_message_dict = {'en': 'This email is already in use.', 'he': 'הדואר האלקטרוני הזה כבר נמצא בשימוש.'}
            _enter_a_valid_date_error_message_dict = {'en': 'Enter a valid date.', 'he': 'יש להזין תאריך חוקי.'}
            _please_enter_a_correct_username_and_password_error_message_dict = {'en': 'Please enter a correct username and password. Note that both fields may be case-sensitive.', 'he': 'נא להזין שם משתמש/ת וסיסמה נכונים. נא לשים לב כי שני השדות רגישים לאותיות גדולות/קטנות.'}
            _your_old_password_was_entered_incorrectly_error_message_dict = {'en': 'Your old password was entered incorrectly. Please enter it again.', 'he': 'סיסמתך הישנה הוזנה בצורה שגויה. נא להזינה שוב.'}
            _the_two_password_fields_didnt_match_error_message_dict = {'en': "The two password fields didn’t match.", 'he': 'שני שדות הסיסמה אינם זהים.'}
            _entity_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, and may contain letters, digits or dashes.', 'he': 'שם המשתמש/ת חייב להתחיל עם 4 אותיות או יותר, ויכול להכיל אותיות, ספרות או מקפים. שם המשתמש/ת חייב להיות באנגלית.'}
            _user_username_must_start_with_4_or_more_letters_error_message_dict = {'en': 'Username must start with 4 or more letters, after which can be any number of digits. You can add dashes between words.', 'he': 'שם המשתמש/ת חייב להתחיל עם 4 אותיות או יותר, לאחר מכן ניתן להוסיף מספר כלשהו של ספרות. ניתן להוסיף מקפים בין מילים. שם המשתמש/ת חייב להיות באנגלית.'}
            _slug_does_not_parse_to_username_error_message_dict = {'en': 'Slug does not parse to username.', 'he': 'slug לא מתאים לשם המשתמש/ת.'}
            _youve_already_confirmed_this_email_address_error_message_dict = {'en': "You've already confirmed this email address.", 'he': 'כבר אימתת את כתובת הדואר האלקטרוני שלך.'}
            _invalid_confirmation_link_error_message_dict = {'en': "Invalid confirmation link.", 'he': 'קישור אימות לא חוקי.'}
            _youve_confirmed_your_email_address_message_dict = {'en': "You've confirmed your email address.", 'he': 'אימתת את כתובת הדואר האלקטרוני שלך.'}
            _the_email_address_was_deleted_error_message_dict = {'en': 'The email address was deleted.', 'he': 'כתובת הדואר האלקטרוני נמחקה.'}
            _you_have_changed_your_primary_email_address_error_message_dict = {'en': 'You have made this email address primary.', 'he': 'הפכת את כתובת הדואר האלקטרוני הזאת לראשית.'}
            _username_is_required_error_message_dict = {'en': 'Username is required.', 'he': 'שם המשתמש/ת נדרש.'}
            _password_reset_on_speedy_net_subject_dict = {'en': "Password reset on Speedy Net", 'he': "איפוס סיסמה בספידי נט"}
            _password_reset_on_speedy_match_subject_dict = {'en': "Password reset on Speedy Match", 'he': "איפוס סיסמה בספידי מץ'"}
            _ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message_dict = {'en': 'Ensure this value is greater than or equal to -32768.', 'he': 'יש לוודא שהערך גדול מ או שווה ל־-32768.'}
            _ensure_this_value_is_less_than_or_equal_to_32767_error_message_dict = {'en': 'Ensure this value is less than or equal to 32767.', 'he': 'יש לוודא שערך זה פחות מ או שווה ל־32767 .'}

            _value_is_not_a_valid_choice_error_message_to_format_dict = {'en': 'Value {value} is not a valid choice.', 'he': 'ערך {value} אינו אפשרות חוקית.'}
            _value_must_be_an_integer_error_message_to_format_dict = {'en': "“{value}” value must be an integer.", 'he': "הערך '{value}' חייב להיות מספר שלם."}
            _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format_dict = {'en': 'Username must contain at least {min_length} alphanumeric characters (it has {value_length}).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {min_length} תווים אלפאנומריים לפחות (מכיל {value_length}). שם המשתמש/ת חייב להיות באנגלית.'}
            _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format_dict = {'en': 'Username must contain at most {max_length} alphanumeric characters (it has {value_length}).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {max_length} תווים אלפאנומריים לכל היותר (מכיל {value_length}). שם המשתמש/ת חייב להיות באנגלית.'}
            _username_must_contain_at_least_min_length_characters_error_message_to_format_dict = {'en': 'Username must contain at least {min_length} characters (it has {value_length}).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {min_length} תווים לפחות (מכיל {value_length}).'}
            _username_must_contain_at_most_max_length_characters_error_message_to_format_dict = {'en': 'Username must contain at most {max_length} characters (it has {value_length}).', 'he': 'נא לוודא ששם המשתמש/ת מכיל {max_length} תווים לכל היותר (מכיל {value_length}).'}
            _a_confirmation_message_was_sent_to_email_address_error_message_to_format_dict = {'en': 'A confirmation message was sent to {email_address}', 'he': 'הודעת אימות נשלחה ל-‎{email_address}‎'}

            _you_cant_change_your_username_error_message_dict_by_gender = {
                'en': {
                    **{gender: "You can't change your username." for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "לא ניתן לשנות שם משתמשת.",
                    User.GENDER_MALE_STRING: "לא ניתן לשנות שם משתמש.",
                    User.GENDER_OTHER_STRING: "לא ניתן לשנות שם משתמש/ת.",
                },
            }
            _confirm_your_email_address_on_speedy_net_subject_dict_by_gender = {
                'en': {
                    **{gender: "Confirm your email address on Speedy Net" for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "אמתי את כתובת הדואר האלקטרוני שלך בספידי נט",
                    User.GENDER_MALE_STRING: "אמת את כתובת הדואר האלקטרוני שלך בספידי נט",
                    User.GENDER_OTHER_STRING: "אמת/י את כתובת הדואר האלקטרוני שלך בספידי נט",
                },
            }
            _confirm_your_email_address_on_speedy_match_subject_dict_by_gender = {
                'en': {
                    **{gender: "Confirm your email address on Speedy Match" for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "אמתי את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                    User.GENDER_MALE_STRING: "אמת את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                    User.GENDER_OTHER_STRING: "אמת/י את כתובת הדואר האלקטרוני שלך בספידי מץ'",
                },
            }

            self._this_field_cannot_be_null_error_message = _this_field_cannot_be_null_error_message_dict[self.language_code]
            self._this_field_cannot_be_blank_error_message = _this_field_cannot_be_blank_error_message_dict[self.language_code]
            self._id_contains_illegal_characters_error_message = _id_contains_illegal_characters_error_message_dict[self.language_code]
            self._value_must_be_valid_json_error_message = _value_must_be_valid_json_error_message_dict[self.language_code]
            self._invalid_password_error_message = _invalid_password_error_message_dict[self.language_code]
            self._password_too_short_error_message = _password_too_short_error_message_dict[self.language_code]
            self._password_too_long_error_message = _password_too_long_error_message_dict[self.language_code]
            self._this_username_is_already_taken_error_message = _this_username_is_already_taken_error_message_dict[self.language_code]
            self._enter_a_valid_email_address_error_message = _enter_a_valid_email_address_error_message_dict[self.language_code]
            self._this_email_is_already_in_use_error_message = _this_email_is_already_in_use_error_message_dict[self.language_code]
            self._enter_a_valid_date_error_message = _enter_a_valid_date_error_message_dict[self.language_code]
            self._please_enter_a_correct_username_and_password_error_message = _please_enter_a_correct_username_and_password_error_message_dict[self.language_code]
            self._your_old_password_was_entered_incorrectly_error_message = _your_old_password_was_entered_incorrectly_error_message_dict[self.language_code]
            self._the_two_password_fields_didnt_match_error_message = _the_two_password_fields_didnt_match_error_message_dict[self.language_code]
            self._entity_username_must_start_with_4_or_more_letters_error_message = _entity_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]
            self._user_username_must_start_with_4_or_more_letters_error_message = _user_username_must_start_with_4_or_more_letters_error_message_dict[self.language_code]
            self._slug_does_not_parse_to_username_error_message = _slug_does_not_parse_to_username_error_message_dict[self.language_code]
            self._youve_already_confirmed_this_email_address_error_message = _youve_already_confirmed_this_email_address_error_message_dict[self.language_code]
            self._invalid_confirmation_link_error_message = _invalid_confirmation_link_error_message_dict[self.language_code]
            self._youve_confirmed_your_email_address_message = _youve_confirmed_your_email_address_message_dict[self.language_code]
            self._the_email_address_was_deleted_error_message = _the_email_address_was_deleted_error_message_dict[self.language_code]
            self._you_have_changed_your_primary_email_address_error_message = _you_have_changed_your_primary_email_address_error_message_dict[self.language_code]
            self._username_is_required_error_message = _username_is_required_error_message_dict[self.language_code]
            self._password_reset_on_speedy_net_subject = _password_reset_on_speedy_net_subject_dict[self.language_code]
            self._password_reset_on_speedy_match_subject = _password_reset_on_speedy_match_subject_dict[self.language_code]
            self._ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message = _ensure_this_value_is_greater_than_or_equal_to_minus_32768_error_message_dict[self.language_code]
            self._ensure_this_value_is_less_than_or_equal_to_32767_error_message = _ensure_this_value_is_less_than_or_equal_to_32767_error_message_dict[self.language_code]

            self._value_is_not_a_valid_choice_error_message_to_format = _value_is_not_a_valid_choice_error_message_to_format_dict[self.language_code]
            self._value_must_be_an_integer_error_message_to_format = _value_must_be_an_integer_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format = _username_must_contain_at_least_min_length_alphanumeric_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format = _username_must_contain_at_most_max_length_alphanumeric_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_least_min_length_characters_error_message_to_format = _username_must_contain_at_least_min_length_characters_error_message_to_format_dict[self.language_code]
            self._username_must_contain_at_most_max_length_characters_error_message_to_format = _username_must_contain_at_most_max_length_characters_error_message_to_format_dict[self.language_code]
            self._a_confirmation_message_was_sent_to_email_address_error_message_to_format = _a_confirmation_message_was_sent_to_email_address_error_message_to_format_dict[self.language_code]

            self._you_cant_change_your_username_error_message_dict_by_gender = _you_cant_change_your_username_error_message_dict_by_gender[self.language_code]
            self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender = _confirm_your_email_address_on_speedy_net_subject_dict_by_gender[self.language_code]
            self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender = _confirm_your_email_address_on_speedy_match_subject_dict_by_gender[self.language_code]

            self.assertSetEqual(set1=set(self._you_cant_change_your_username_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))

            self.assertEqual(first=len(set(self._you_cant_change_your_username_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._confirm_your_email_address_on_speedy_net_subject_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._confirm_your_email_address_on_speedy_match_subject_dict_by_gender.keys())), second=3)

            self.assertEqual(first=len(set(self._user_all_the_required_fields_keys())), second=7)
            self.assertEqual(first=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), second=set(self._user_all_the_required_fields_keys()))
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys())), second=7)
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()) - set(self._user_all_the_required_fields_keys())), second=0)
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value=None).keys()), set2=set(self._user_all_the_required_fields_keys()) | {'first_name_en', 'first_name_he'})
            self.assertEqual(first=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()), second=set(self._user_all_the_required_fields_keys()))
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys())), second=7)
            self.assertEqual(first=len(set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()) - set(self._user_all_the_required_fields_keys())), second=0)
            self.assertSetEqual(set1=set(self._cannot_create_user_without_all_the_required_fields_errors_dict_by_value(value='').keys()), set2=set(self._user_all_the_required_fields_keys()) | {'first_name_en', 'first_name_he'})
            self.assertListEqual(list1=self._profile_form_all_the_required_fields_keys(), list2=[field_name for field_name in self._registration_form_all_the_required_fields_keys() if (not (field_name in ['email', 'new_password1']))])
            self.assertSetEqual(set1=set(self._registration_form_all_the_required_fields_keys()) - {'email', 'new_password1'}, set2=set(self._profile_form_all_the_required_fields_keys()))
            self.assertSetEqual(set1=set(self._profile_form_all_the_required_fields_keys()) | {'email', 'new_password1'}, set2=set(self._registration_form_all_the_required_fields_keys()))
            self.assertNotEqual(first=[to_attribute(name='first_name')], second=['first_name'])
            self.assertNotEqual(first=[to_attribute(name='first_name'), to_attribute(name='last_name')], second=['first_name', 'last_name'])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:2], list2=[to_attribute(name='first_name', language_code=language_code) for language_code, language_name in django_settings.LANGUAGES])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:2], list2=[to_attribute(name='first_name', language_code='en'), to_attribute(name='first_name', language_code='he')])
            self.assertListEqual(list1=self._user_all_the_required_fields_keys()[:2], list2=['first_name_en', 'first_name_he'])
            self.assertListEqual(list1=self._registration_form_all_the_required_fields_keys()[:1], list2=[to_attribute(name='first_name')])
            self.assertListEqual(list1=self._profile_form_all_the_required_fields_keys()[:1], list2=[to_attribute(name='first_name')])

        def assert_required_fields_and_errors_dict(self, required_fields, errors_dict):
            self.assertSetEqual(set1=set(errors_dict.keys()), set2=set(required_fields))
            self.assertDictEqual(d1=errors_dict, d2=self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=required_fields))

        def assert_registration_form_required_fields(self, required_fields):
            self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._registration_form_all_the_required_fields_are_required_errors_dict())

        def assert_profile_form_required_fields(self, required_fields):
            self.assert_required_fields_and_errors_dict(required_fields=required_fields, errors_dict=self._profile_form_all_the_required_fields_are_required_errors_dict())


