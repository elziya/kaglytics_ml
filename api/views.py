import logging
import os
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import SignUpSerializer, EmailVerifySerializer, SignInSerializer, CompetitionDtoSerializer, \
    CategorySerializer, RewardTypeSerializer, TagSerializer
from .models import User, VerifyCode, Category, RewardType, Tag
from .services import api_competitions_to_df, active_competitions_to_dto_list, get_active_competitions, \
    get_filtered_active_competitions, get_competitions_categories_stats, get_competitions_organizations_stats, \
    get_competitions_reward_type_stats, get_competitions_tags_stats
from .utils import Util, generate_code


@permission_classes([])
class SignUpView(generics.GenericAPIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        code = generate_code()
        verify_code = VerifyCode(code=code, user=user)
        verify_code.save()

        absurl = f"{os.environ.get('FRONT_URL')}/email-verify?code=" + str(code)
        email_body = 'Hi ' + user.username + '. Use the link below to to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Verify your email'}

        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def competitions_categories_stat_view(request):
    dictionary = get_competitions_categories_stats()
    return Response(dictionary, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_organizations_stat_view(request):
    dictionary = get_competitions_organizations_stats()
    return Response(dictionary, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_reward_type_stat_view(request):
    dictionary = get_competitions_reward_type_stats()
    return Response(dictionary, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_tags_stat_view(request):
    dictionary = get_competitions_tags_stats()
    return Response(dictionary, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_view(request):
    api_active_competitions = get_active_competitions()
    active_competitions_df = api_competitions_to_df(api_active_competitions)
    active_competitions = active_competitions_to_dto_list(active_competitions_df)
    serializer = CompetitionDtoSerializer(active_competitions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_search_view(request):
    title = request.query_params.get('title')
    category_str = request.query_params.get('categories')
    reward_type_str = request.query_params.get('reward_types')
    deadline_before_str = request.query_params.get('deadline_before')
    deadline_after_str = request.query_params.get('deadline_after')
    tags_str = request.query_params.get('tags')

    if title.lower() == "null":
        title = None

    deadline_before = None
    if deadline_before_str:
        try:
            deadline_before = datetime.strptime(deadline_before_str, '%Y-%m-%d')
        except ValueError:
            print(logging.INFO, 'Invalid deadline_before format. Expected format: YYYY-MM-DD.')
    deadline_after = None
    if deadline_after_str:
        try:
            deadline_after = datetime.strptime(deadline_after_str, '%Y-%m-%d')
        except ValueError:
            print(logging.INFO, 'Invalid deadline_after format. Expected format: YYYY-MM-DD.')
    tags = None
    if tags_str:
        tags = tags_str.split(',')
        if tags[0].lower() == "null":
            tags = None
    reward_types = None
    if reward_type_str:
        reward_types = reward_type_str.split(',')
        if reward_types[0].lower() == "null":
            reward_types = None
    categories = None
    if category_str:
        categories = category_str.split(',')
        if categories[0].lower() == "null":
            categories = None

    api_filtered_competitions = get_filtered_active_competitions(title=title, categories=categories,
                                                                 reward_types=reward_types,
                                                                 deadline_before=deadline_before,
                                                                 deadline_after=deadline_after, tags=tags)
    if len(api_filtered_competitions) > 0:
        active_competitions_df = api_competitions_to_df(api_filtered_competitions)
        active_competitions = active_competitions_to_dto_list(active_competitions_df)
        serializer = CompetitionDtoSerializer(active_competitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(None, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_categories_view(request):
    available_competitions_categories = Category.objects.all()
    serializer = CategorySerializer(available_competitions_categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_reward_types_view(request):
    available_competitions_reward_types = RewardType.objects.all()
    serializer = RewardTypeSerializer(available_competitions_reward_types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def competitions_tags_view(request):
    available_competitions_tags = Tag.objects.all()
    serializer = TagSerializer(available_competitions_tags, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([])
class EmailVerifyView(generics.GenericAPIView):
    serializer_class = EmailVerifySerializer

    def post(self, request):
        code = request.data['code']

        try:
            verify_code = VerifyCode.objects.get(code=code)
            user = User.objects.get(id=verify_code.user_id)

            if not user.is_verified:
                user.is_verified = True
                user.save()

            verify_code.delete()

            return Response(user.tokens(), status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'An error has occurred. Please follow the link again'},
                            status=status.HTTP_404_NOT_FOUND)


@permission_classes([])
class SignInView(TokenObtainPairView):
    serializer_class = SignInSerializer
