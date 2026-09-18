"""Évalue la pipeline sur le jeu de test sauvegardé et génère le rapport Markdown.

Réutilise exactement le split produit par `train_model.py` (aucun recalcul de
découpage), afin de garantir la traçabilité de l'évaluation.
"""

import json

import pandas as pd
from sklearn.metrics import confusion_matrix, roc_auc_score

import joblib

from config import (
    DATA_PATH,
    EVALUATION_REPORT_PATH,
    FEATURE_COLUMNS,
    PIPELINE_PATH,
    REPORTS_DIR,
    RISK_THRESHOLD,
    SPLIT_INDICES_PATH,
    TARGET_COLUMN,
)


def compute_metrics(y_true, y_pred, y_score):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    roc_auc = roc_auc_score(y_true, y_score) if len(set(y_true)) > 1 else float("nan")

    return {
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
    }


def format_report(model_metrics: dict, baseline_metrics: dict, n_test: int) -> str:
    return f"""# Rapport d'évaluation — modèle de scoring de risque de churn

Évalué sur un jeu de test de **{n_test} clients**, jamais utilisé pour
l'entraînement ni pour l'ajustement du prétraitement. Seuil de décision : {RISK_THRESHOLD}.

Ces résultats mesurent la performance du modèle sur ce jeu de test précis ; ils
ne garantissent pas la même performance sur d'autres données.

## Matrice de confusion (modèle)

| | Prédit non-churn | Prédit churn |
| --- | --- | --- |
| **Réel non-churn** | {model_metrics['tn']} | {model_metrics['fp']} |
| **Réel churn** | {model_metrics['fn']} | {model_metrics['tp']} |

## Métriques (modèle, classe churn = 1)

| Métrique | Valeur |
| --- | --- |
| Exactitude (accuracy) | {model_metrics['accuracy']:.3f} |
| Précision | {model_metrics['precision']:.3f} |
| Rappel | {model_metrics['recall']:.3f} |
| F1-score | {model_metrics['f1']:.3f} |
| ROC-AUC | {model_metrics['roc_auc']:.3f} |

## Lecture en effectifs

- Résiliations réellement survenues dans le jeu de test : {model_metrics['tp'] + model_metrics['fn']}
- Résiliations **détectées** par le modèle (vrais positifs) : {model_metrics['tp']}
- Résiliations **manquées** par le modèle (faux négatifs) : {model_metrics['fn']}
- **Fausses alertes** (clients signalés à risque mais non churnés, faux positifs) : {model_metrics['fp']}

## Comparaison au modèle de référence « toujours non-churn »

| Métrique | Modèle | Baseline (toujours non-churn) |
| --- | --- | --- |
| Exactitude (accuracy) | {model_metrics['accuracy']:.3f} | {baseline_metrics['accuracy']:.3f} |
| Précision (classe churn) | {model_metrics['precision']:.3f} | {baseline_metrics['precision']:.3f} |
| Rappel (classe churn) | {model_metrics['recall']:.3f} | {baseline_metrics['recall']:.3f} |
| F1-score (classe churn) | {model_metrics['f1']:.3f} | {baseline_metrics['f1']:.3f} |

La baseline ne prédit jamais de churn : sa précision et son rappel pour la
classe churn sont nuls par construction, quelle que soit la qualité réelle
des données. Son exactitude reflète uniquement la proportion de clients
non-churnés dans le jeu de test.

## Portée et limites

Ce score est une estimation pédagogique produite par une régression
logistique sur 5 variables. Il ne constitue pas une probabilité calibrée, ni
une garantie de résiliation ou de fidélité, et n'a pas d'horizon temporel
documenté.
"""


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    with open(SPLIT_INDICES_PATH, encoding="utf-8") as f:
        split_indices = json.load(f)
    test_index = split_indices["test_index"]

    X_test = df.loc[test_index, FEATURE_COLUMNS]
    y_test = df.loc[test_index, TARGET_COLUMN]

    pipeline = joblib.load(PIPELINE_PATH)
    y_score = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_score >= RISK_THRESHOLD).astype(int)

    model_metrics = compute_metrics(y_test, y_pred, y_score)

    baseline_pred = pd.Series(0, index=y_test.index)
    baseline_metrics = compute_metrics(y_test, baseline_pred, baseline_pred)

    report = format_report(model_metrics, baseline_metrics, n_test=len(test_index))

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(EVALUATION_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"Rapport sauvegardé dans {EVALUATION_REPORT_PATH}")


if __name__ == "__main__":
    main()
