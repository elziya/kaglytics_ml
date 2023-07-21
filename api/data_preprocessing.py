import pandas as pd

from api.models import Category, Organization, EvaluationMetric, RewardType

DELETED_COLUMNS = ['Id', 'Slug', 'ForumId', 'CompetitionTypeId', 'TeamModelDeadlineDate', 'ModelSubmissionDeadlineDate',
                   'FinalLeaderboardHasBeenVerified', 'HasKernels', 'OnlyAllowKernelSubmissions', 'HasLeaderboard',
                   'LeaderboardPercentage', 'LeaderboardDisplayFormat', 'EvaluationAlgorithmAbbreviation',
                   'EvaluationAlgorithmDescription', 'EvaluationAlgorithmIsMax', 'NumScoredSubmissions',
                   'BanTeamMergers', 'EnableTeamModels', 'NumPrizes', 'UserRankMultiplier', 'CanQualifyTiers',
                   'ValidationSetName', 'ValidationSetValue', 'EnableSubmissionModelHashes',
                   'EnableSubmissionModelAttachments', 'HostName', 'TotalTeams', 'TotalSubmissions']

RENAMED_COLUMNS = {'Subtitle': 'description', 'HostSegmentTitle': 'category', 'DeadlineDate': 'deadline',
                   'ProhibitNewEntrantsDeadlineDate': 'newEntrantDeadline', 'TeamMergerDeadlineDate': 'mergerDeadline',
                   'EvaluationAlgorithmName': 'evaluationMetric'}

DATE_COLUMNS = ['deadline', 'newentrantdeadline', 'mergerdeadline', 'enableddate']

CAT_FEATURES = ['category', 'organizationname', 'evaluationmetric', 'rewardtype']
TEXT_FEATURES = ['title', 'description']

DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'


def fill_string_na(df, features):
    for feature in features:
        df[feature].fillna('', inplace=True)


def create_new_features(df):
    df['duration'] = (df['deadline'] - df["enableddate"]).dt.days
    df['day_to_new'] = (df['deadline'] - df["newentrantdeadline"]).dt.days
    df['day_to_team'] = (df['deadline'] - df["mergerdeadline"]).dt.days

    df.drop(columns=['deadline', 'newentrantdeadline', 'mergerdeadline', 'enableddate'], inplace=True)


def preprocess_data(df):
    df.drop(columns=DELETED_COLUMNS, inplace=True)

    df.rename(columns=RENAMED_COLUMNS, inplace=True)

    df.columns = map(str.lower, df.columns)

    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(df[column], format=DATETIME_FORMAT)

    create_new_features(df)

    df['day_to_new'].fillna(df.mode()['day_to_new'][0], inplace=True)
    df['day_to_team'].fillna(df.mode()['day_to_team'][0], inplace=True)

    df['rewardquantity'].fillna(0, inplace=True)

    fill_string_na(df, CAT_FEATURES)
    fill_string_na(df, TEXT_FEATURES)
    df.replace('nan', '', inplace=True)

    x = df.drop(['totalcompetitors'], axis=1)
    y = df['totalcompetitors']

    return x, y


def replace_non_existent_categories(df, row, names):
    if str(row) not in names:
        df.replace(row, '', inplace=True)


def preprocess_active_competitions(df):

    for column in DATE_COLUMNS:
        df[column].fillna(df['deadline'], inplace=True)

    create_new_features(df)

    df['day_to_new'].fillna(df.mode()['day_to_new'][0], inplace=True)
    df['day_to_team'].fillna(df.mode()['day_to_team'][0], inplace=True)

    categories_names = map(lambda x: x.name, Category.objects.all())
    organization_names = map(lambda x: x.name, Organization.objects.all())
    evaluation_metric_names = map(lambda x: x.name, EvaluationMetric.objects.all())
    reward_type_names = map(lambda x: x.name, RewardType.objects.all())

    for index, row in df.iterrows():

        replace_non_existent_categories(df, row['category'], categories_names)
        replace_non_existent_categories(df, row['organizationname'], organization_names)
        replace_non_existent_categories(df, row['evaluationmetric'], evaluation_metric_names)
        replace_non_existent_categories(df, row['rewardtype'], reward_type_names)
