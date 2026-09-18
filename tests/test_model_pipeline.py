import json

import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from config import (
    DATA_PATH,
    FEATURE_COLUMNS,
    NON_PREDICTIVE_COLUMNS,
    PIPELINE_PATH,
    RANDOM_SEED,
    SPLIT_INDICES_PATH,
    TARGET_COLUMN,
    TEST_SIZE,
)


@pytest.fixture(scope="module")
def df():
    return pd.read_csv(DATA_PATH)


@pytest.fixture(scope="module")
def split_indices():
    with open(SPLIT_INDICES_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_target_never_in_features():
    assert TARGET_COLUMN not in FEATURE_COLUMNS


def test_non_predictive_columns_excluded():
    for column in NON_PREDICTIVE_COLUMNS:
        assert column not in FEATURE_COLUMNS


def test_split_is_reproducible(df):
    from sklearn.model_selection import train_test_split

    train_1, test_1 = train_test_split(
        df.index, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=df[TARGET_COLUMN]
    )
    train_2, test_2 = train_test_split(
        df.index, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=df[TARGET_COLUMN]
    )

    assert list(train_1) == list(train_2)
    assert list(test_1) == list(test_2)


def test_saved_split_matches_recomputed_split(df, split_indices):
    from sklearn.model_selection import train_test_split

    train_index, test_index = train_test_split(
        df.index, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=df[TARGET_COLUMN]
    )

    assert sorted(split_indices["train_index"]) == sorted(train_index.tolist())
    assert sorted(split_indices["test_index"]) == sorted(test_index.tolist())


def test_train_and_test_do_not_overlap(split_indices):
    train_set = set(split_indices["train_index"])
    test_set = set(split_indices["test_index"])
    assert train_set.isdisjoint(test_set)


def test_pipeline_is_saved_and_loadable():
    import joblib

    pipeline = joblib.load(PIPELINE_PATH)
    assert isinstance(pipeline, Pipeline)


def test_pipeline_scores_are_valid_probabilities(df, split_indices):
    import joblib

    pipeline = joblib.load(PIPELINE_PATH)
    X_test = df.loc[split_indices["test_index"], FEATURE_COLUMNS]

    scores = pipeline.predict_proba(X_test)[:, 1]

    assert ((scores >= 0.0) & (scores <= 1.0)).all()
