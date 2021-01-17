from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from .serializers import UserSerializer, PromoSerializer, AuthenticationSerializer
from .serializers import CommentedAccountsSerializer, CommentedAccountSerializer
from . import models
from django.contrib.auth import authenticate
from .utils import add_to_queue
from datetime import datetime
import pytz

# Create your views here.

class UserAPIView(views.APIView):
  """APIView for getting and creating Users"""

  serializer_class = UserSerializer

  def get_queryset(self):
    return models.User.objects.all()

  def get(self, request, format=None):
    try:
      user_id = request.query_params['id']
      if(user_id != None):
        user = models.User.objects.get(id=user_id)
        user_serializer = UserSerializer(user)
    except Exception as e:
      print(e)
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

  serializer_class = PromoSerializer

  def get_queryset(self):
    return models.Promo_Account.objects.all()

  def get(self, request, format=None):
    try:
      promo_id = request.query_params['id']
      if(promo_id != None):
        promo_account = models.Promo_Account.objects.get(id=promo_id)
        promo_serializer = PromoSerializer(promo_account)
    except Exception as e:
      print(e)
      promo_accounts = self.get_queryset()
      promo_serializer = PromoSerializer(promo_accounts, many=True)
    return Response(promo_serializer.data)

  def post(self, request, format=None):
    '''post a promo and add it to the recurring queue.
    to_run_at must be in utc time!'''

    user_username = request.data['user']

    request.data['user'] = models.User.objects.get(username=user_username).id

    promo_serializer = PromoSerializer(data=request.data)
    time_to_run = datetime.strptime(request.data['to_run_at'], '%Y-%m-%dT%H:%M')
    add_to_queue(request.data['promo_username'], request.data['promo_password'],
     request.data['target_account'], request.data['proxy'],
      time_to_run)

    if promo_serializer.is_valid():
      promo_serializer.save()
      return Response({"message": "saved", "data": promo_serializer.data})
    else:
      return Response({"message": "invalid", "data": promo_serializer.errors})



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
    post username and password in body
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
      return Response({"message": "invalid", "data": auth_serializer})