# Rapport d'évaluation — modèle de scoring de risque de churn

Évalué sur un jeu de test de **180 clients**, jamais utilisé pour
l'entraînement ni pour l'ajustement du prétraitement. Seuil de décision : 0.5.

Ces résultats mesurent la performance du modèle sur ce jeu de test précis ; ils
ne garantissent pas la même performance sur d'autres données.

## Matrice de confusion (modèle)

| | Prédit non-churn | Prédit churn |
| --- | --- | --- |
| **Réel non-churn** | 146 | 4 |
| **Réel churn** | 13 | 17 |

## Métriques (modèle, classe churn = 1)

| Métrique | Valeur |
| --- | --- |
| Exactitude (accuracy) | 0.906 |
| Précision | 0.810 |
| Rappel | 0.567 |
| F1-score | 0.667 |
| ROC-AUC | 0.913 |

## Lecture en effectifs

- Résiliations réellement survenues dans le jeu de test : 30
- Résiliations **détectées** par le modèle (vrais positifs) : 17
- Résiliations **manquées** par le modèle (faux négatifs) : 13
- **Fausses alertes** (clients signalés à risque mais non churnés, faux positifs) : 4

## Comparaison au modèle de référence « toujours non-churn »

| Métrique | Modèle | Baseline (toujours non-churn) |
| --- | --- | --- |
| Exactitude (accuracy) | 0.906 | 0.833 |
| Précision (classe churn) | 0.810 | 0.000 |
| Rappel (classe churn) | 0.567 | 0.000 |
| F1-score (classe churn) | 0.667 | 0.000 |

La baseline ne prédit jamais de churn : sa précision et son rappel pour la
classe churn sont nuls par construction, quelle que soit la qualité réelle
des données. Son exactitude reflète uniquement la proportion de clients
non-churnés dans le jeu de test.

## Portée et limites

Ce score est une estimation pédagogique produite par une régression
logistique sur 5 variables. Il ne constitue pas une probabilité calibrée, ni
une garantie de résiliation ou de fidélité, et n'a pas d'horizon temporel
documenté.
