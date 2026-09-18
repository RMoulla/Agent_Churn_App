"""Validation partagée entre le formulaire et l'import CSV (exigence F-04).

Les mêmes règles s'appliquent quelle que soit l'origine des données : un
client saisi au formulaire ou une ligne d'un fichier importé.
"""

import math

import pandas as pd

from config import FEATURE_COLUMNS

INTEGER_COLUMNS = {"Age", "Num_Sites"}
NON_NEGATIVE_COLUMNS = {"Age", "Total_Purchase", "Years", "Num_Sites"}
BINARY_COLUMNS = {"Account_Manager"}


def _validate_numeric_value(column: str, raw_value):
    """Valide et convertit une valeur brute pour une colonne du modèle.

    Retourne un tuple (valeur_convertie, message_erreur) ; un seul des deux
    éléments est renseigné.
    """
    if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == "") or (
        not isinstance(raw_value, str) and pd.isna(raw_value)
    ):
        return None, f"la colonne « {column} » est manquante"

    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return None, f"la colonne « {column} » doit être numérique"

    if not math.isfinite(value):
        return None, f"la colonne « {column} » doit être un nombre fini"

    if column in INTEGER_COLUMNS and not value.is_integer():
        return None, f"la colonne « {column} » doit être un nombre entier"

    if column in NON_NEGATIVE_COLUMNS and value < 0:
        return None, f"la colonne « {column} » doit être positive ou nulle"

    if column in BINARY_COLUMNS and value not in (0, 1):
        return None, f"la colonne « {column} » doit valoir 0 ou 1"

    if column in INTEGER_COLUMNS or column in BINARY_COLUMNS:
        value = int(value)

    return value, None


def validate_record(raw_record) -> tuple[dict, list[str]]:
    """Valide les 5 variables d'un client (formulaire ou ligne de fichier).

    `raw_record` doit exposer `.get(colonne)` (dict ou pandas.Series).
    Retourne (valeurs_converties, erreurs) ; `valeurs_converties` n'est
    complet que si `erreurs` est vide.
    """
    values = {}
    errors = []
    for column in FEATURE_COLUMNS:
        value, error = _validate_numeric_value(column, raw_record.get(column))
        if error:
            errors.append(error[0].upper() + error[1:] + ".")
        else:
            values[column] = value
    return values, errors


def validate_dataframe(df: pd.DataFrame) -> list[str]:
    """Valide un fichier CSV importé. Retourne la liste des erreurs (vide si valide)."""
    if df.empty:
        return ["Le fichier est vide."]

    missing_columns = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing_columns:
        return [
            f"La colonne obligatoire « {column} » est absente du fichier."
            for column in missing_columns
        ]

    errors = []
    for row_position, (_, row) in enumerate(df.iterrows(), start=1):
        _, row_errors = validate_record(row)
        errors.extend(f"Ligne {row_position} : {error}" for error in row_errors)
    return errors
