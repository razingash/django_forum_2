from django.urls import path
from .views import *

urlpatterns = [
    path('', RulesPage.as_view(), name='home'),
    path('profile/<int:profile_id>/', ProfilePage.as_view(), name='profile'),
    path('profile/<int:profile_id>/friends/', ProfileFriendsPage.as_view(), name='profile_friends'),
    path('profile/<int:profile_id>/bans/', ProfileBansPage.as_view(), name='profile_bans'),
    path('profile/<int:profile_id>/events/', ProfileEventsPage.as_view(), name='profile_events'),
    path('profile/<int:profile_id>/contribution/', ProfileContributionPage.as_view(), name='profile_contribution'),
    path('discussions/', DiscussionsPage.as_view(), name='discussions'),
    path('discussion/<int:discussion_id>/', DiscussionPage.as_view(), name='discussion'),
    path('discussion-new/', DiscussionCreatePage.as_view(), name='new_discussion'),
    path('register/', RegistrationPage.as_view(), name='registration'),
    path('login/', LoginPage.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('settings/base/', SettingsBasePage.as_view(), name='base_settings'),
    path('settings/password/', SettingsPasswordPage.as_view(), name='password_settings'),
]

