from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url('user', views.UserAPIView.as_view()),
    url('promo', views.PromoAPIView.as_view()),
    url('commentedaccounts', views.CommentedAccountsAPIView.as_view()),
    url('authenticate', views.AuthenticationAPIView.as_view()),
    url('activate', views.ActivateAPIView.as_view()),
    url('deactivate', views.DeactivateAPIView.as_view())
]