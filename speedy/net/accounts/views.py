import logging

from django.contrib import messages
from django.contrib.sites.models import Site
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import pgettext_lazy, ugettext as _

from speedy.core.accounts import views as speedy_core_accounts_views

logger = logging.getLogger(__name__)


class IndexView(speedy_core_accounts_views.IndexView):
    registered_redirect_to = 'profiles:me'


class ActivateSiteProfileView(speedy_core_accounts_views.ActivateSiteProfileView):
    def get_account_activation_url(self):
        return reverse_lazy('accounts:activate')

    def display_welcome_message(self):
        site = Site.objects.get_current()
        messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Welcome to {site_name}! Your account is now active.').format(site_name=_(site.name)))

    def form_valid(self, form):
        super().form_valid(form=form)
        success_url = self.get_success_url()
        if (self.request.user.speedy_net_profile.is_active):
            self.display_welcome_message()
            site = Site.objects.get_current()
            logger.info('User {user} activated their account on {site_name}.'.format(site_name=_(site.name), user=self.request.user))
        return redirect(to=success_url)


