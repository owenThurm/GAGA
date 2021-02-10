from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url('user/promoaccounts', views.UserPromoAccountsAPIView.as_view()),
    url('promo/deactivateall', views.DeactivateAllAPIView.as_view()),
    url('promo/dequeue', views.DequeuePromoAccountAPIView.as_view()),
    url('user/resetpassword', views.ResetPasswordAPIView.as_view()),
    url('user/customcomments', views.CustomCommentPoolAPIView.as_view()),
    url('user/setcustomcomments', views.SetCommentPoolAPIView.as_view()),
    url('user/authenticate', views.AuthenticationAPIView.as_view()),
    url('user/getidentity', views.TokenIdentityAPIView.as_view()),
    url('user', views.UserAPIView.as_view()),
    url('promo', views.PromoAPIView.as_view()),
    url('commentedaccounts', views.CommentedAccountsAPIView.as_view()),
    url('deactivate', views.DeactivateAPIView.as_view()),
    url('activate', views.ActivateAPIView.as_view()),
    url('review', views.SetProxyAPIView.as_view()),
]