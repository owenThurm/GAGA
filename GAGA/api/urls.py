from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url('user', views.UserAPIView.as_view()),
    url('promo', views.PromoAPIView.as_view()),
]