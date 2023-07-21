import re
import pandas as pd
import collections
import joblib

from api.kaggle_api import api
from .dto import TagDto
from .models import Tag, Category, Competition, Organization, RewardType
from .utils import extract_active_competition_from_row
from .data_preprocessing import preprocess_active_competitions
from .prediction_model import FITTED_MODEL_FILENAME


def get_competitions_categories_stats():
    categories = Category.objects.all()
    dictionary = {}

    for category in categories:
        dictionary[category.name] = len(Competition.objects.filter(category=category))

    return dictionary


def get_competitions_organizations_stats():
    organizations = Organization.objects.all()
    counter = collections.Counter()

    for organization in organizations:
        counter[organization.name] = len(Competition.objects.filter(organization=organization))

    return dict(counter.most_common(10))


def get_competitions_reward_type_stats():
    reward_types = RewardType.objects.all()
    dictionary = {}

    for reward_type in reward_types:
        dictionary[reward_type.name] = len(Competition.objects.filter(rewardType=reward_type))

    return dictionary


def get_competitions_tags_stats():
    tags = Tag.objects.all()
    counter = collections.Counter()

    for tag in tags:
        counter[tag.name] = len(Competition.objects.filter(tags__id=tag.id))

    return dict(counter.most_common(10))


def get_active_competitions():
    api_competitions = api.competitions_list()
    return api_competitions


def get_filtered_active_competitions(title=None, categories=None, reward_types=None, deadline_before=None,
                                     deadline_after=None, tags=None):
    competitions = api.competitions_list()

    if title is not None:
        competitions = [c for c in competitions if title.lower() in c.title.lower()]

    if categories is not None:
        competitions = [c for c in competitions if contains_category(c.category.lower(), categories)]

    if reward_types is not None:
        competitions = [c for c in competitions if contains_reward_type(c.reward.lower(), reward_types)]

    if deadline_before is not None:
        competitions = [c for c in competitions if deadline_before >= c.deadline]

    if deadline_after is not None:
        competitions = [c for c in competitions if deadline_after <= c.deadline]

    if tags is not None:
        competitions = [c for c in competitions if
                        all(tag.lower() in map(lambda t: t.name.lower(), c.tags) for tag in tags)]

    return competitions


def contains_category(category, categories):
    for c in categories:
        if c.lower() == category.lower():
            return True
    return False


def contains_reward_type(reward_type, reward_types):
    for rt in reward_types:
        if rt.lower() == reward_type.lower():
            return True
        if rt.lower() == "usd" and reward_type.lower().startswith("$"):
            return True
        if rt.lower() == "eur" and reward_type.lower().startswith("€"):
            return True
    return False


def active_competitions_to_dto_list(df_competitions):
    competitions = []

    tag_names = list(df_competitions.columns.values)
    tag_names = tag_names[14:]

    predictions = get_total_competitors_prediction(df_competitions)

    for index, row in df_competitions.iterrows():
        new_competition_dto = extract_active_competition_from_row(row).to_dto()
        new_competition_dto.set_prediction(predictions[index])

        competition_tags = list()
        for tag in tag_names:
            if row[tag] == 1:
                try:
                    c_tag = Tag.objects.get(name=tag).to_dto()
                except Tag.DoesNotExist:
                    c_tag = TagDto(sid=0, kaggle_id=0, name=tag)
                competition_tags.append(c_tag)

        new_competition_dto.tags_dto = competition_tags
        competitions.append(new_competition_dto)

    return competitions


def get_total_competitors_prediction(df_competitions):
    df = df_competitions.copy()
    preprocess_active_competitions(df)
    model = joblib.load(f"api/models/{FITTED_MODEL_FILENAME}")
    predictions = model.predict(df)
    predictions = [int(x) for x in predictions]
    return predictions


def api_competitions_to_df(competitions):
    api_competitions = competitions
    comp_list = []
    for c in api_competitions:
        comp_list.append(vars(c))

    feature_names = ['title', 'description', 'category', 'organizationname', 'evaluationmetric', 'maxdailysubmissions',
                     'maxteamsize', 'reward', 'deadline', 'enableddate', 'tags', 'id', 'mergerdeadline',
                     'newentrantdeadline']

    active_df = pd.DataFrame(comp_list)
    active_df.columns = map(str.lower, active_df.columns)
    active_df = pd.DataFrame(active_df, columns=feature_names)

    reward_type = []
    reward_quantity = []
    for index, row in active_df.iterrows():

        if re.match(r'(\$)', row['reward']):
            s = re.match(r'(?:\$)(.+)', row['reward']).group(1).replace(',', '')
            reward_type.append('USD')
            reward_quantity.append(int(s))

        elif re.match(r'(\€)', row['reward']):
            s = re.match(r'(?:€)(.+)', row['reward']).group(1).replace(',', '')
            reward_type.append('EUR')
            reward_quantity.append(int(s))

        else:
            reward_type.append(row['reward'])
            reward_quantity.append(0)

    active_df.insert(loc=7, column='rewardtype', value=reward_type)
    active_df.insert(loc=8, column='rewardquantity', value=reward_quantity)

    tags_names = map(lambda t: t.name, Tag.objects.all())

    for tag in tags_names:
        tag_list = []
        for index, row in active_df.iterrows():
            row['tags'] = map(lambda t: str(t), row['tags'])
            tag_list.append(1 if tag in row['tags'] else 0)
        active_df[tag] = tag_list

    active_df.drop(columns=['tags', 'reward'], inplace=True)
    return active_df
