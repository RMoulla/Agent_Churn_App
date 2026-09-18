"""Entraîne la pipeline de scoring (prétraitement + régression logistique).

Sauvegarde la pipeline entraînée et les indices du split train/test, afin que
`evaluate_model.py` réutilise exactement le même découpage (traçabilité,
reproductibilité).
"""

import json

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import joblib

from config import (
    DATA_PATH,
    FEATURE_COLUMNS,
    MODEL_DIR,
    PIPELINE_PATH,
    RANDOM_SEED,
    SPLIT_INDICES_PATH,
    TARGET_COLUMN,
    TEST_SIZE,
)


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    train_index, test_index = train_test_split(
        df.index,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=y,
    )

    X_train, y_train = X.loc[train_index], y.loc[train_index]

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(random_state=RANDOM_SEED)),
        ]
    )
    pipeline.fit(X_train, y_train)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, PIPELINE_PATH)

    with open(SPLIT_INDICES_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "train_index": train_index.tolist(),
                "test_index": test_index.tolist(),
            },
            f,
        )

    print(f"Pipeline entraînée sur {len(train_index)} clients, sauvegardée dans {PIPELINE_PATH}")
    print(f"Indices du split sauvegardés dans {SPLIT_INDICES_PATH}")


if __name__ == "__main__":
    main()
