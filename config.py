"""Constantes partagées par l'entraînement, l'évaluation et l'interface."""

from pathlib import Path

# Emplacement du fichier historique (lecture seule, jamais modifié)
DATA_PATH = Path(__file__).parent / "customer_churn.csv"

# Les 5 variables prédictives, et uniquement celles-ci (voir AGENTS.md)
FEATURE_COLUMNS = ["Age", "Total_Purchase", "Account_Manager", "Years", "Num_Sites"]

# Cible : jamais utilisée comme variable d'entrée du modèle
TARGET_COLUMN = "Churn"

# Colonnes d'identification/métadonnées : jamais des prédicteurs
NON_PREDICTIVE_COLUMNS = ["Names", "Company", "Onboard_date", "Location"]

# Seuil de décision (convention pédagogique, pas un seuil métier optimisé)
RISK_THRESHOLD = 0.5

# Graine fixe pour tout tirage aléatoire (split, modèle)
RANDOM_SEED = 42

# Proportion du jeu de test lors du split
TEST_SIZE = 0.2

# Artefacts générés
MODEL_DIR = Path(__file__).parent / "model"
PIPELINE_PATH = MODEL_DIR / "pipeline.joblib"
SPLIT_INDICES_PATH = MODEL_DIR / "split_indices.json"

REPORTS_DIR = Path(__file__).parent / "reports"
EVALUATION_REPORT_PATH = REPORTS_DIR / "evaluation_report.md"
