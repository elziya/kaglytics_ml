"""kaglytics URL Configuration

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import SignUpView, competitions_view, EmailVerifyView, SignInView, competitions_search_view, \
    competitions_categories_view, competitions_reward_types_view, competitions_tags_view, \
    competitions_categories_stat_view, competitions_organizations_stat_view, competitions_reward_type_stat_view, \
    competitions_tags_stat_view

urlpatterns = [
    path('sign-up', SignUpView.as_view()),
    path('sign-in', SignInView.as_view()),
    path('refresh-token', TokenRefreshView.as_view()),
    path('competitions/active', competitions_view),
    path('competitions/active/search', competitions_search_view),
    path('competitions/categories', competitions_categories_view),
    path('competitions/reward-types', competitions_reward_types_view),
    path('competitions/tags', competitions_tags_view),
    path('email-verify', EmailVerifyView.as_view()),
    path('competitions/statistics/categories', competitions_categories_stat_view),
    path('competitions/statistics/organizations', competitions_organizations_stat_view),
    path('competitions/statistics/rewardtypes', competitions_reward_type_stat_view),
    path('competitions/statistics/tags', competitions_tags_stat_view)
]
