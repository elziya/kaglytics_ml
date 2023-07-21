from catboost import Pool
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split

FITTED_MODEL_FILENAME = 'fitted_model.sav'


def split_data(x, y, test_size):
    return train_test_split(x, y, test_size=test_size, random_state=13)


def create_pools(x, y, test_size, cat_features, text_features):
    x_train, x_test, y_train, y_test = split_data(x, y, test_size)
    train_pool = Pool(
        x_train, y_train,
        cat_features=cat_features,
        text_features=text_features,
    )
    validation_pool = Pool(
        x_test, y_test,
        cat_features=cat_features,
        text_features=text_features,
    )
    return train_pool, validation_pool


def get_model(**kwargs):
    return CatBoostRegressor(
        iterations=1000,
        learning_rate=0.05,
        **kwargs
    )


def fit_model(model, train_pool, validation_pool):
    model.fit(
        train_pool,
        eval_set=validation_pool,
        verbose=100,
    )
