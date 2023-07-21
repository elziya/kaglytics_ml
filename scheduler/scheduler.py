import os
import sys
import zipfile
from datetime import datetime
import joblib

import numpy as np
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

from api.kaggle_api import api
from api.models import Competition, Tag
from api.utils import extract_competition_from_row
from api.data_preprocessing import preprocess_data, CAT_FEATURES, TEXT_FEATURES
from api.prediction_model import create_pools, fit_model, FITTED_MODEL_FILENAME, get_model


def update_competitions_info_file():
    print("Start updating competitions info file...")

    zip_file_path = "./api/data/Competitions.csv.zip"
    competition_file_path = "./api/data/Competitions.csv"
    competition_tags_file_path = "./api/data/CompetitionTags.csv"

    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    if os.path.exists(competition_file_path):
        os.remove(competition_file_path)
    if os.path.exists(competition_tags_file_path):
        os.remove(competition_tags_file_path)

    api.dataset_download_file('Kaggle/meta-kaggle', 'Competitions.csv', path="./api/data")
    with zipfile.ZipFile("./api/data/Competitions.csv.zip", 'r') as zip_ref:
        zip_ref.extractall("./api/data")
    api.dataset_download_file('Kaggle/meta-kaggle', 'CompetitionTags.csv', path="./api/data")

    df_competitions = pd.read_csv("./api/data/Competitions.csv")
    df_competitions_tags = pd.read_csv("./api/data/CompetitionTags.csv")
    df_tags = pd.read_csv("./api/data/Tags.csv")
    df_organizations = pd.read_csv("./api/data/Organizations.csv")

    tags_columns = set(df_competitions_tags['TagId'])
    for index, row in df_competitions_tags.iterrows():
        df_competitions.loc[df_competitions['Id'] == row['CompetitionId'], str(row['TagId'])] = 1

    for tag in tags_columns:
        df_competitions[str(tag)] = np.where(df_competitions[str(tag)] != 1, 0, 1)

    for index, row in df_tags.iterrows():
        df_competitions = df_competitions.rename(columns={str(row['Id']): row['Name']})

    df_competitions['OrganizationId'] = df_competitions['OrganizationId'].astype(str)
    for index, row in df_organizations.iterrows():
        df_competitions.loc[df_competitions['OrganizationId'] == str(float(row['Id'])), 'OrganizationId'] = row['Name']

    df_competitions = df_competitions.rename(columns={'OrganizationId': 'OrganizationName'})
    df_competitions.to_csv("./api/data/out.csv", sep=',', encoding='utf-8', index=False)
    print("Competitions info file updated successfully.")


def update_competitions_info_table():
    print("Start updating competitions info table...")

    df_competitions = pd.read_csv("api/data/out.csv", low_memory=False)
    tag_names = list(df_competitions.columns.values)
    tag_names = tag_names[42:]

    for index, row in df_competitions.iterrows():
        deadline_date_object = datetime.strptime(row['DeadlineDate'], '%m/%d/%Y %H:%M:%S')
        if deadline_date_object.year == datetime.now().year:
            new_competition = extract_competition_from_row(row)
            competitions = Competition.objects.filter(kaggle_id=new_competition.kaggle_id)
            if competitions.count() > 1:
                for i in range(1, competitions.count()):
                    competitions[i].delete()
                new_competition.id = competitions[0].id
                new_competition.save()
            elif competitions.count() == 0:
                new_competition.save()

                competition_tags = list()
                for tag in tag_names:
                    if row[tag] == 1:
                        competition_tags.append(Tag.objects.get(name=tag))
                new_competition.tags.set(competition_tags)

                print(f"Updated table. Add competition with id {new_competition.id}")
        else:
            continue
    print("Competitions info table updated successfully.")


def fit_model_with_new_data():
    print("Start fitting model with new data...")

    model = get_model(cat_features=CAT_FEATURES, text_features=TEXT_FEATURES)
    data = pd.read_csv("api/data/out.csv", low_memory=False)
    x, y = preprocess_data(data)
    train_pool, validation_pool = create_pools(x, y, 0.25, CAT_FEATURES, TEXT_FEATURES)
    fit_model(model, train_pool, validation_pool)

    joblib.dump(model, f"./api/models/{FITTED_MODEL_FILENAME}")
    print("Model was fitted successfully.")


def start():

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(update_competitions_info_file, 'interval', hours=24, name='update_competitions_info_file',
                      jobstore='default')
    scheduler.add_job(update_competitions_info_table, 'interval', hours=24, name='update_competitions_info_table',
                      jobstore='default')
    scheduler.add_job(fit_model_with_new_data, 'interval', hours=24, name='fit_model_with_new_data',
                      jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)
