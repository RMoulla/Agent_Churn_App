"""Chargement de la pipeline et calcul du score/alerte (F-01, F-02, F-08).

La pipeline est chargée une seule fois par processus et jamais ré-entraînée.
"""

from functools import lru_cache

import joblib
import pandas as pd

from config import FEATURE_COLUMNS, PIPELINE_PATH, RISK_THRESHOLD


class ModelNotFoundError(RuntimeError):
    """Levée quand la pipeline entraînée n'est pas disponible sur disque."""


@lru_cache(maxsize=1)
def load_pipeline():
    if not PIPELINE_PATH.exists():
        raise ModelNotFoundError(
            "Aucun modèle entraîné n'a été trouvé. "
            "Lancez d'abord « python train_model.py »."
        )
    return joblib.load(PIPELINE_PATH)


def score_record(pipeline, values: dict) -> float:
    """Calcule le score de risque (entre 0 et 1) pour un client."""
    row = pd.DataFrame([[values[column] for column in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    return float(pipeline.predict_proba(row)[0, 1])


def alert_label(score: float) -> str:
    return "Risque élevé" if score >= RISK_THRESHOLD else "Risque faible"
