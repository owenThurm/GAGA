from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from .services.promo_account_service import PromoAccountService
from .services.user_service import UserService
from . import models
from django.contrib.auth import authenticate
from . import serializers
from .utils import add_to_queue
from datetime import datetime
import pytz

promo_account_service = PromoAccountService()
user_service = UserService()

# Create your views here.
class UserAPIView(views.APIView):
  """APIView for getting and creating Users"""

  serializer_class = serializers.UserSerializer

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
        user_serializer = serializers.UserSerializer(user)
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
          user_serializer = serializers.UserSerializer(user)
          return Response(user_serializer.data)
    except Exception as e:
      pass
    users = self.get_queryset()
    user_serializer = serializers.UserSerializer(users, many=True)
    return Response(user_serializer.data)

  def post(self, request, format=None):
    print('called post, request: ', request.data)
    user_serializer = serializers.UserSerializer(data=request.data)

    if user_serializer.is_valid():
      user_serializer.save()
      return Response({'message': 'saved', 'data': user_serializer.data})
    else:
      return Response({"message": "invalid user", "data": user_serializer.data})

class PromoAPIView(views.APIView):
  """APIView for Promo Accounts"""
  serializer_class = serializers.GetPromoSerializer

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
        promo_serializer = serializers.GetPromoSerializer(promo_account)
    except Exception as e:
      print(e)
      promo_accounts = self.get_queryset()
      promo_serializer = serializers.GetPromoSerializer(promo_accounts, many=True)
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
    promo_serializer = serializers.PostPromoSerializer(data=request.data)

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

    update_promo_serializer = serializers.UpdatePromoSerializer(data=request.data)

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

  serializer_class = serializers.CommentedAccountsSerializer

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

    commented_accounts_serializer = serializers.CommentedAccountsSerializer(data=request.data)


    if commented_accounts_serializer.is_valid():
      promo_account = models.Promo_Account.objects.get(promo_username=request.data['promo_username'])
      user = promo_account.user
      for account in request.data['commented_on_accounts']:
        commented_on_account_data = {
          'commented_on_account_username': account,
          'user': user.id
        }
        commented_on_account_serializer = serializers.CommentedAccountSerializer(data=commented_on_account_data)
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

  serializer_class = serializers.AuthenticationSerializer

  def post(self, request, format=None):
    '''
    post email and password in body
    returns true if authenticated, false if not.
    '''
    auth_serializer = serializers.AuthenticationSerializer(data=request.data)

    if auth_serializer.is_valid():
      # authenticate
      user_email = auth_serializer.data['email']
      user_password = auth_serializer.data['password']
      user_username = user_service.authenticate_user(user_email, user_password)
      if user_username is None:
        # did not pass authentication
        return Response({"message": "invalid credentials", "authenticated": False})
      else:
        return Response({
          "message": "successfully authenticated",
          "authenticated": True,
          "data": user_username,
        })
    else:
      return Response({"message": "invalid", "data": auth_serializer.data})

class ActivateAPIView(views.APIView):
  '''An APIView for activating promo accounts'''

  class_serializers = serializers.PromoUsernameSerializer

  def post(self, request, format=None):
    '''expects a promo_username in the body'''

    activation_serializer = serializers.PromoUsernameSerializer(data=request.data)

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

  class_serializer = serializers.PromoUsernameSerializer

  def post(self, request, format=None):
    '''expects a promo_username in the body'''
    deactivation_serializer = serializers.PromoUsernameSerializer(data=request.data)

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


    dequeue_serializer = serializers.PromoUsernameSerializer(data=request.data)

    if dequeue_serializer.is_valid():

      dequeued_promo_username = request.data.get('promo_username')
      promo_account_service.dequeue_promo_account(dequeued_promo_username)

      return Response({"message": "Dequeued account", "data": dequeued_promo_username})

    else:
      return Response({"message": "invalid", "data": dequeue_serializer.data})


class SetProxyAPIView(views.APIView):
  '''Sets the Proxy for an account'''

  class_serializer = serializers.AddProxySerializer

  def post(self, request, format=None):
    '''
    expects the following body format:

    {
      "promo_username": "promoaccountusername1",
      "proxy": "127.323.543.564.788..."
    }
    '''

    proxy_review_serializer = serializers.AddProxySerializer(data=request.data)

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

  class_serializer = serializers.GetUserPromoAccountsSerializer

  def post(self, request, format=None):
    '''
    Expects the following body format
    {
      "username": "genuine apparel growth user username"
    }
    '''
    user_serializer = serializers.GetUserPromoAccountsSerializer(data=request.data)

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

  class_serializer = serializers.ResetPasswordSerializer

  def post(self, request, format=None):
    '''
    Expects the following body format

    {
      "username": "owenthurm",
      "new_password": "password123"
    }
    '''

    reset_password_serializer = serializers.ResetPasswordSerializer(data=request.data)

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

class SetCommentPoolAPIView(views.APIView):
  '''
    Used to set the comment pool for an account
    -- either custom pool or default pool
  '''

  serializer_class = serializers.SetCommentPoolSerializer

  def post(self, request, format=None):
    '''
      expects the following body:

      {
        "user_username": "upcomingstreetwearfashion",
        "using_custom_comments": false
      }
    '''

    update_comment_pool_serializer = serializers.SetCommentPoolSerializer(data=request.data)

    if update_comment_pool_serializer.is_valid():
      user_username = request.data['user_username']
      using_custom_comments = request.data['using_custom_comments']
      if not user_service.user_is_custom_comment_eligible(user_username) and using_custom_comments:
        return Response({"message": "user is not eligible for custom comments",
                         "data": update_comment_pool_serializer.data})
      try:
        user_service.update_user_comment_pool_setting(user_username, using_custom_comments)
      except Exception as e:
        return Response({"message": "Couldn't find a user corresponding to username",
        "data": update_comment_pool_serializer.data})
      return Response({"message": "updated", "data": update_comment_pool_serializer.data})
    else:
      return Response({"message": "invalid", "data": update_comment_pool_serializer.data})

class CustomCommentPoolAPIView(views.APIView):
  '''
    Used to add a list of custom comments to a
    user's custom comment pool
  '''

  def get_queryset(self):
    return models.CustomComment.objects.all()

  def get(self, request, format=None):
    '''
      Used to get a single user's custom comment pool
      if a user's username is passed in the query params
      and used to get all custom comments if not.

      expects ?user=owenthurm

      in query params
    '''
    try:
      user_username = request.query_params['user']
      if user_username != None:
        try:
          custom_comments = user_service.get_user_custom_comment_pool(user_username)
          custom_comments_serializer = serializers.GetCustomCommentSerializer(custom_comments, many=True)

          return Response({"message": user_username + "'s comment pool",
                            "data": custom_comments_serializer.data})
        except Exception as e:
          print(e)
          return Response({"message": "could not find comment pool corresponding to user",
                           "data": user_username})
    except Exception as e:
      custom_comments = self.get_queryset()
      custom_comments_serializer = serializers.GetCustomCommentSerializer(custom_comments, many=True)
      return Response(custom_comments_serializer.data)


  class_serializer = serializers.AddCustomCommentsSerializer

  def post(self, request, format=None):
    '''
      expects the following body:

      {
        "user_username": "owenthurm"
        "new_custom_comments": ["hey what's good, shoot me a dm when you can",
                                "what's up, dm me whenever you can", ...]
      }
    '''

    new_comments_serializer = serializers.AddCustomCommentsSerializer(data=request.data)

    if new_comments_serializer.is_valid():
      user_username = request.data['user_username']
      new_custom_comments = request.data['new_custom_comments']
      comments_are_unique = user_service.comments_are_unique(user_username, new_custom_comments)
      if not comments_are_unique:
        duplicate_comment_text = user_service.get_duplicate_comment(user_username, new_custom_comments)
        return Response({"message": "Comments are not unique", "data": duplicate_comment_text})
      try:
        user_service.add_to_user_custom_comment_pool(user_username, new_custom_comments)
      except Exception as e:
        print(e)
        return Response({"message": "Couldn't find a user corresponding to username",
                         "data": new_comments_serializer.data})
      return Response({"message": "updated", "data": new_comments_serializer.data})
    else:
      return Response({"message": "invalid", "data": new_comments_serializer.data})

  def delete(self, request, format=None):
    '''
      expects the following body:

      {
        "user_username": "owenthurm",
        "custom_comment_text": "Hey what's up! Shoot us a dm when you can!"
      }
    '''

    delete_custom_comment_serializer = serializers.DeleteCustomCommentSerializer(data=request.data)

    if delete_custom_comment_serializer.is_valid():
      user_username = request.data['user_username']
      custom_comment_text = request.data['custom_comment_text']
      try:
        user_service.delete_custom_comment(user_username, custom_comment_text)
        if not user_service.user_is_custom_comment_eligible(user_username):
          user_service.update_user_comment_pool_setting(user_username, False)
      except Exception as e:
        return Response({"message": "Couldn't locate custom comment with that text for given user",
                         "data": delete_custom_comment_serializer.data})
      return Response({"message": "deleted", "data": delete_custom_comment_serializer.data})
    else:
      return Response({"message": "invalid", "data": delete_custom_comment_serializer.data})

  def put(self, request, format=None):
    '''
      expects the following body format:

      {
        "user_username": "owenthurm",
        "old_custom_comment_text": "",
        "new_custom_comment_text": ""
      }
    '''

    update_custom_comment_serializer = serializers.UpdateCustomCommentSerializer(data=request.data)

    if update_custom_comment_serializer.is_valid():
      user_username = request.data['user_username']
      old_custom_comment_text = request.data['old_custom_comment_text']
      new_custom_comment_text = request.data['new_custom_comment_text']
      try:
        user_service.update_custom_comment_text(user_username, old_custom_comment_text,
                                                          new_custom_comment_text)
      except Exception as e:
        return Response({"message": "Couldn't find comment to update from given user",
                        "data": update_custom_comment_serializer.data})
      return Response({"message": "updated", "data": update_custom_comment_serializer.data})
    else:
      return Response({"message": "invalid", "data": update_custom_comment_serializer.data})