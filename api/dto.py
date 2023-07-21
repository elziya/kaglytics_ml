from datetime import datetime
from typing import List


class TagDto:
    def __init__(self, sid: int, kaggle_id: int, name: str):
        self.sid = sid
        self.kaggle_id = kaggle_id
        self.name = name


class CategoryDto:
    def __init__(self, sid: int, name: str):
        self.sid = sid
        self.name = name


class OrganizationDto:
    def __init__(self, sid: int, kaggle_id: int, name: str):
        self.sid = sid
        self.kaggle_id = kaggle_id
        self.name = name


class EvaluationMetricDto:
    def __init__(self, sid: int, name: str):
        self.sid = sid
        self.name = name


class RewardTypeDto:
    def __init__(self, sid: int, name: str):
        self.sid = sid
        self.name = name


class CompetitionDto:
    def __init__(self, sid: int, kaggle_id: int, title: str, description: str, category_dto: CategoryDto,
                 organization_dto: OrganizationDto,evaluation_metric_dto: EvaluationMetricDto,
                 max_daily_submissions: int, max_team_size: int, reward_type_dto: RewardTypeDto, reward_quantity: int,
                 total_teams: int, total_competitors: int, total_submissions: int, enabled_date: datetime,
                 deadline: datetime, tags_dto: List[TagDto]):
        self.prediction = 0
        self.sid = sid
        self.kaggle_id = kaggle_id
        self.title = title
        self.description = description
        self.category_dto = category_dto
        self.organization_dto = organization_dto
        self.evaluation_metric_dto = evaluation_metric_dto
        self.max_daily_submissions = max_daily_submissions
        self.max_team_size = max_team_size
        self.reward_type_dto = reward_type_dto
        self.reward_quantity = reward_quantity
        self.total_teams = total_teams
        self.total_competitors = total_competitors
        self.total_submissions = total_submissions
        self.enabled_date = enabled_date
        self.deadline = deadline
        self.tags_dto = tags_dto

    def set_prediction(self, prediction):
        self.prediction = prediction

