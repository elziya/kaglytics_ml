from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken

from api.dto import TagDto, CategoryDto, OrganizationDto, EvaluationMetricDto, RewardTypeDto, CompetitionDto


class Tag(models.Model):
    kaggle_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)

    def to_dto(self):
        return TagDto(
            sid=self.id,
            kaggle_id=self.kaggle_id,
            name=self.name,
        )

    @staticmethod
    def from_dto(dto: TagDto):
        return Tag(
            id=dto.sid,
            kaggle_id=dto.kaggle_id,
            name=dto.name,
        )


class Category(models.Model):
    name = models.CharField(max_length=100)

    def to_dto(self):
        return CategoryDto(
            sid=self.id,
            name=self.name,
        )

    @staticmethod
    def from_dto(dto: CategoryDto):
        return Category(
            id=dto.sid,
            name=dto.name,
        )


class Organization(models.Model):
    kaggle_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)

    def to_dto(self):
        return OrganizationDto(
            sid=self.id,
            kaggle_id=self.kaggle_id,
            name=self.name,
        )

    @staticmethod
    def from_dto(dto: OrganizationDto):
        return Organization(
            id=dto.sid,
            kaggle_id=dto.kaggle_id,
            name=dto.name,
        )


class EvaluationMetric(models.Model):
    name = models.CharField(max_length=250)

    def to_dto(self):
        return EvaluationMetricDto(
            sid=self.id,
            name=self.name,
        )

    @staticmethod
    def from_dto(dto: EvaluationMetricDto):
        return EvaluationMetric(
            id=dto.sid,
            name=dto.name,
        )


class RewardType(models.Model):
    name = models.CharField(max_length=100)

    def to_dto(self):
        return RewardTypeDto(
            sid=self.id,
            name=self.name,
        )

    @staticmethod
    def from_dto(dto: RewardTypeDto):
        return RewardType(
            id=dto.sid,
            name=dto.name,
        )


class Competition(models.Model):
    kaggle_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=250)
    description = models.TextField(null=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    evaluationMetric = models.ForeignKey(EvaluationMetric, null=True, on_delete=models.SET_NULL)
    maxDailySubmissions = models.IntegerField()
    maxTeamSize = models.IntegerField()
    rewardType = models.ForeignKey(RewardType, null=True, on_delete=models.SET_NULL)
    rewardQuantity = models.IntegerField(default=0)
    totalTeams = models.IntegerField()
    totalCompetitors = models.IntegerField(null=True, blank=True)
    totalSubmissions = models.IntegerField(null=True, blank=True)
    enabledDate = models.DateTimeField()
    deadline = models.DateTimeField()
    tags = models.ManyToManyField(Tag)

    def to_dto(self):
        return CompetitionDto(
            sid=self.id,
            kaggle_id=self.kaggle_id,
            title=self.title,
            description=self.description,
            category_dto=Category.to_dto(self.category),
            organization_dto=Organization.to_dto(self.organization),
            evaluation_metric_dto=EvaluationMetric.to_dto(self.evaluationMetric),
            max_daily_submissions=self.maxDailySubmissions,
            max_team_size=self.maxTeamSize,
            reward_type_dto=RewardType.to_dto(self.rewardType),
            reward_quantity=self.rewardQuantity,
            total_teams=self.totalTeams,
            total_competitors=self.totalCompetitors,
            total_submissions=self.totalSubmissions,
            enabled_date=self.enabledDate,
            deadline=self.deadline,
            tags_dto=list()
        )


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=False, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class VerifyCode(models.Model):
    code = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

