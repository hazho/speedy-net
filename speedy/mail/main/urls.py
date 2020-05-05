from django.urls import re_path

from . import views

app_name = 'speedy.mail.main'
urlpatterns = [
    re_path(route=r'', view=views.MainPageView.as_view(), name='main_page'),
]


