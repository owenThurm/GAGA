from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from .serializers import UserSerializer, PostPromoSerializer, AuthenticationSerializer
from .serializers import CommentedAccountsSerializer, CommentedAccountSerializer
from .serializers import PromoUsernameSerializer, AddProxySerializer, GetPromoSerializer
from .serializers import GetUserPromoAccountsSerializer, ResetPasswordSerializer, UpdatePromoSerializer
from .services.promo_account_service import PromoAccountService
from . import models
from django.contrib.auth import authenticate
from .utils import add_to_queue
from datetime import datetime
import pytz

promo_account_service = PromoAccountService()

# Create your views here.
class UserAPIView(views.APIView):
  """APIView for getting and creating Users"""

  serializer_class = UserSerializer

  def get_queryset(self):
    return models.User.objects.all()

  def get(self, request, format=None):
    try:
      user_username = request.query_params['username']
      if(user_username != None):
        try:
          user = models.User.objects.get(username=user_username)
        except Exception as e:
          return Response({"message": "No user corresponding to username: " + user_username})
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)
    except Exception as e:
      pass
    try:
        user_email = request.query_params['email']
        if(user_email != None):
          try:
            user = models.User.objects.get(email=user_email)
          except Exception as e:
            return Response({"message": "No user corresponding to email: " + user_email})
          user_serializer = UserSerializer(user)
          return Response(user_serializer.data)
    except Exception as e:
      pass
    users = self.get_queryset()
    user_serializer = UserSerializer(users, many=True)
    return Response(user_serializer.data)

  def post(self, request, format=None):
    print('called post, request: ', request.data)
    user_serializer = UserSerializer(data=request.data)

    if user_serializer.is_valid():
      user_serializer.save()
      return Response({'message': 'saved', 'data': user_serializer.data})
    else:
      return Response({"message": "invalid user", "data": user_serializer.data})

class PromoAPIView(views.APIView):
  """APIView for Promo Accounts"""
  serializer_class = GetPromoSerializer

  def get_queryset(self):
    return models.Promo_Account.objects.all()

  def get(self, request, format=None):
    try:
      promo_username = request.query_params['username']
      if(promo_username != None):
        try:
          promo_account = models.Promo_Account.objects.get(promo_username=promo_username)
        except Exception as e:
          return Response({"message": "No promo account corresponding to username: " + promo_username})
        promo_serializer = GetPromoSerializer(promo_account)
    except Exception as e:
      print(e)
      promo_accounts = self.get_queryset()
      promo_serializer = GetPromoSerializer(promo_accounts, many=True)
    return Response(promo_serializer.data)

  def post(self, request, format=None):
    '''post a promo and set it for review'''
    '''
    Expects the following format:

    {
      promo_username: "promo account username",
      promo_password: "promo account password",
      promo_target: "promo target account",
      user: "Growth Automation user username who owns promo account"
    }
    '''

    user_username = request.data['user']
    request.data['user'] = models.User.objects.get(username=user_username).id
    promo_serializer = PostPromoSerializer(data=request.data)

    if promo_serializer.is_valid():
      promo_serializer.save()
      return Response({"message": "saved", "data": promo_serializer.data})
    else:
      return Response({"message": "invalid", "data": promo_serializer.errors})

  def put(self, request, format=None):
    '''update a promo account and set it for review'''

    '''
      Expects the following body:

      {
        "old_promo_username": "upcomingstreetwearfashion",
        "new_promo_username": "genuineaesthetic",
        "new_promo_password": "password123",
        "new_promo_target": "riotsociety",
      }
    '''

    update_promo_serializer = UpdatePromoSerializer(data=request.data)

    if update_promo_serializer.is_valid():
      old_promo_username = request.data['old_promo_username']
      new_promo_username = request.data['new_promo_username']
      new_promo_password = request.data['new_promo_password']
      new_promo_target = request.data['new_promo_target']
      promo_account_service.update_promo_account(old_promo_username, new_promo_username,
                                                 new_promo_password, new_promo_target)

      return Response({"message": "updated", "data": update_promo_serializer.data})
    else:
      return Response({"message": "invalid", "data": update_promo_serializer.data})


class CommentedAccountsAPIView(views.APIView):
  '''APIView for adding and accessing commented on accounts for each user'''

  serializer_class = CommentedAccountsSerializer

  def post(self, request, format=None):
    '''Takes a list of strings, where each string is the username of an
    account that has been commented on by the user'''

    '''
    body format:

    {
      "promo_username": "genuineaesthetic"
      "commented_on_accounts": ["commented_on_account_1_username",
                                "commented_on_account_2_username", ...]
    }'''
    print(request.data)

    commented_accounts_serializer = CommentedAccountsSerializer(data=request.data)


    if commented_accounts_serializer.is_valid():
      promo_account = models.Promo_Account.objects.get(promo_username=request.data['promo_username'])
      user = promo_account.user
      for account in request.data['commented_on_accounts']:
        commented_on_account_data = {
          'commented_on_account_username': account,
          'user': user.id
        }
        commented_on_account_serializer = CommentedAccountSerializer(data=commented_on_account_data)
        if commented_on_account_serializer.is_valid():
          commented_on_account_serializer.save()
          print('saved', commented_on_account_data)
          print(commented_on_account_serializer.data)
        else:
          print('invalid', commented_on_account_data)
          print(commented_on_account_serializer.data)


      return Response({"message": "saved", "data": commented_accounts_serializer.data})
    else:
      return Response({"message": "invalid", "data": commented_accounts_serializer.data})

class AuthenticationAPIView(views.APIView):
  '''An APIView for authenticating users'''

  serializer_class = AuthenticationSerializer

  def post(self, request, format=None):
    '''
    post email and password in body
    returns true if authenticated, false if not.
    '''
    auth_serializer = AuthenticationSerializer(data=request.data)

    if auth_serializer.is_valid():
      # authenticate
      user = authenticate(email=auth_serializer.data['email'], password=auth_serializer.data['password'])
      if user is None:
        # did not pass authentication
        return Response({"message": "invalid credentials", "authenticated": False})
      else:
        return Response({"message": "successfully authenticated", "authenticated": True})
    else:
      return Response({"message": "invalid", "data": auth_serializer.data})

class ActivateAPIView(views.APIView):
  '''An APIView for activating promo accounts'''

  class_serializers = PromoUsernameSerializer

  def post(self, request, format=None):
    '''expects a promo_username in the body'''

    activation_serializer = PromoUsernameSerializer(data=request.data)

    if activation_serializer.is_valid():
      promo_username = request.data['promo_username']
      promo_account = models.Promo_Account.objects.get(promo_username= promo_username)
      if not promo_account.under_review:
        if not promo_account.is_queued:
          print(f'adding {promo_username} to the queue')
          add_to_queue(promo_username, promo_account.promo_password,
          promo_account.target_account, promo_account.proxy)
          promo_account.is_queued = True
          if not promo_account.activated:
            promo_account.activated = True
          promo_account.save()
        elif not promo_account.activated:
          promo_account.activated = True
          promo_account.save()
        return Response({"message": "activated", "data": activation_serializer.data})
      else:
        return Response({"message": "under review", "data": activation_serializer.data})
    else:
      return Response({"message": "invalid", "data": activation_serializer.data})

class DeactivateAPIView(views.APIView):
  '''An APIView for deactivating promo accounts'''

  class_serializer = PromoUsernameSerializer

  def post(self, request, format=None):
    '''expects a promo_username in the body'''
    deactivation_serializer = PromoUsernameSerializer(data=request.data)

    if deactivation_serializer.is_valid():
      promo_username = request.data['promo_username']
      try:
        promo_account_service.deactivate_promo_account(promo_username)
      except Exception as e:
        return Response({"message": "no promo corresponding to promo username", "data": promo_username})

      return Response({"message": "deactivated", "data": deactivation_serializer.data})
    else:
      return Response({"message": "invalid", "data": deactivation_serializer.data})

class DeactivateAllAPIView(views.APIView):
  '''Used to deactivate all promo accounts'''

  def post(self, request, format=None):
    '''expects no body'''
    promo_account_service.deactivate_all_promo_accounts()
    return Response({"message": "Deactivated all promo accounts"})

class DequeuePromoAccountAPIView(views.APIView):
  '''Take a promo account out of the commenting queue'''

  def post(self, request, format=None):
    '''
        expects a promo_username in the body

        {
          "promo_username": "genuineaesthetic"
        }
    '''


    dequeue_serializer = PromoUsernameSerializer(data=request.data)

    if dequeue_serializer.is_valid():

      dequeued_promo_username = request.data.get('promo_username')
      promo_account_service.dequeue_promo_account(dequeued_promo_username)

      return Response({"message": "Dequeued account", "data": dequeued_promo_username})

    else:
      return Response({"message": "invalid", "data": dequeue_serializer.data})


class SetProxyAPIView(views.APIView):
  '''Sets the Proxy for an account'''

  class_serializer = AddProxySerializer

  def post(self, request, format=None):
    '''
    expects the following body format:

    {
      "promo_username": "promoaccountusername1",
      "proxy": "127.323.543.564.788..."
    }
    '''

    proxy_review_serializer = AddProxySerializer(data=request.data)

    if proxy_review_serializer.is_valid():

      try:
        reveiwing_promo_account = models.Promo_Account.objects.get(
          promo_username=proxy_review_serializer.data['promo_username'])
      except Exception as e:
        return Response({
          "message": "invalid",
          "data": "no promo account corresponding to name: "
          + proxy_review_serializer.data['promo_username']
        })

      for account in models.Promo_Account.objects.all():
        if account.proxy == proxy_review_serializer.data['proxy']:
          return Response({"message": "proxy already in use",
          "data": "proxy being used by promo: " + account.promo_username})
      reveiwing_promo_account.proxy = proxy_review_serializer.data['proxy']
      reveiwing_promo_account.under_review = False
      reveiwing_promo_account.save()
      return Response({"message": "reviewed and updated proxy", "data": proxy_review_serializer.data})
    else:
      return Response({"message": "invalid", "data": proxy_review_serializer.data})

class UserPromoAccountsAPIView(views.APIView):
  '''Used to get a list of the promo accounts associated with a user'''

  class_serializer = GetUserPromoAccountsSerializer

  def post(self, request, format=None):
    '''
    Expects the following body format
    {
      "username": "genuine apparel growth user username"
    }
    '''
    user_serializer = GetUserPromoAccountsSerializer(data=request.data)

    if user_serializer.is_valid():
      try:
        user = models.User.objects.get(username=user_serializer.data['username'])
      except Exception as e:
        return Response({"message": "invalid",
         "data": "No user corresponding to username: " + user_serializer.data['username'] })
      promo_accounts = []

      for promo_account in user.promo_account_set.all():
        promo_accounts.append(str(promo_account))

      return Response({"message": "promo accounts", "data": promo_accounts})
    else:
      return Response({"message": "invalid", "data": user_serializer.data})

class ResetPasswordAPIView(views.APIView):
  '''Used to reset the password for a growth automation user'''

  class_serializer = ResetPasswordSerializer

  def post(self, request, format=None):
    '''
    Expects the following body format

    {
      "username": "owenthurm",
      "new_password": "password123"
    }
    '''

    reset_password_serializer = ResetPasswordSerializer(data=request.data)

    if reset_password_serializer.is_valid():
      user_manager = models.UserManager()
      user_username = request.data['username']
      new_password = request.data['new_password']
      try:
        user_manager.set_password(user_username, new_password)
      except Exception as e:
        print(e)
        return Response({"message": "Issue changing password"})
      return Response({"message": "password updated", "data": user_username})
    else:
      return Response({"message": "invalid", "data": reset_password_serializer.data})