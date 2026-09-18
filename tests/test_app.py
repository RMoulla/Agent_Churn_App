"""Tests fonctionnels de l'interface Flask, avec le client de test Flask.

Numérotation reprise de la proposition validée (T1-T11), complétée par des
cas supplémentaires (cohérence formulaire/CSV, seuil non arrondi, valeurs
non finies, fichier à en-têtes seules, démonstration avec le CSV historique,
preuve d'absence de ré-entraînement).
"""

import csv
import io
import re

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

import app as app_module
import config
import scoring

VALID_FORM = {
    "Age": "42",
    "Total_Purchase": "11066.8",
    "Account_Manager": "0",
    "Years": "7.22",
    "Num_Sites": "8",
}

CSV_ONE_CLIENT = (
    "Age,Total_Purchase,Account_Manager,Years,Num_Sites\n"
    "42,11066.8,0,7.22,8\n"
)

CSV_THREE_CLIENTS_WITH_DUPLICATE_NAMES = (
    "Names,Company,Age,Total_Purchase,Account_Manager,Years,Num_Sites\n"
    "Alice Martin,Harvey LLC,42,11066.8,0,7.22,8\n"
    "Bob Martin,Miller LLC,38,12884.75,0,6.67,12\n"
    "Alice Martin,AutreCo,29,5000,1,2.5,5\n"
)


class _FakePipeline:
    """Pipeline factice pour imposer un score précis, sans passer par le modèle réel."""

    def __init__(self, score: float):
        self._score = score

    def predict_proba(self, X):
        return np.array([[1 - self._score, self._score]])


@pytest.fixture(autouse=True)
def _clear_import_store():
    app_module._IMPORT_STORE.clear()
    yield
    app_module._IMPORT_STORE.clear()


@pytest.fixture
def client():
    app_module.app.testing = True
    with app_module.app.test_client() as test_client:
        yield test_client


def _csv_upload(content: str, filename: str = "clients.csv"):
    return {"fichier": (io.BytesIO(content.encode("utf-8")), filename)}


def _session_token(client):
    with client.session_transaction() as sess:
        return sess.get("import_token")


# --- T1/T2 : formulaire individuel ---------------------------------------


def test_t1_form_valid_values_returns_score_and_alert(client):
    response = client.post("/", data=VALID_FORM)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert re.search(r"Score de risque : <strong>[\d.]+ %</strong>", html)
    assert re.search(r"Alerte : <strong>Risque (élevé|faible)</strong>", html)


def test_t2_form_invalid_values_returns_field_errors(client):
    data = {"Age": "-5", "Total_Purchase": "abc", "Account_Manager": "2", "Years": "7.22", "Num_Sites": "8.5"}
    response = client.post("/", data=data)
    html = response.get_data(as_text=True)

    assert "La colonne « Age » doit être positive ou nulle." in html
    assert "La colonne « Total_Purchase » doit être numérique." in html
    assert "La colonne « Account_Manager » doit valoir 0 ou 1." in html
    assert "La colonne « Num_Sites » doit être un nombre entier." in html
    assert "Score de risque" not in html


# --- T3/T4 : import CSV valide ---------------------------------------------


def test_t3_import_valid_with_names_and_company(client):
    response = client.post(
        "/import", data=_csv_upload(CSV_THREE_CLIENTS_WITH_DUPLICATE_NAMES),
        content_type="multipart/form-data", follow_redirects=True,
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Alice Martin" in html
    assert "Bob Martin" in html
    assert "Harvey LLC" in html
    assert "<th>Nom</th>" in html
    assert "<th>Société</th>" in html


def test_t4_import_valid_without_optional_columns(client):
    response = client.post(
        "/import", data=_csv_upload(CSV_ONE_CLIENT),
        content_type="multipart/form-data", follow_redirects=True,
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<th>Nom</th>" not in html
    assert "<th>Société</th>" not in html


# --- T5/T6/T7 : rejets d'import ---------------------------------------------


def test_t5_import_missing_required_column_rejected(client):
    csv_content = "Age,Total_Purchase,Account_Manager,Years\n42,1000,0,5\n"
    response = client.post("/import", data=_csv_upload(csv_content), content_type="multipart/form-data")
    html = response.get_data(as_text=True)

    assert "La colonne obligatoire « Num_Sites » est absente du fichier." in html


def test_t6_import_empty_file_rejected(client):
    response = client.post("/import", data=_csv_upload(""), content_type="multipart/form-data")
    html = response.get_data(as_text=True)

    assert "Le fichier est vide." in html


def test_t7_import_invalid_values_rejected_with_row_and_column(client):
    csv_content = (
        "Age,Total_Purchase,Account_Manager,Years,Num_Sites\n"
        "42,11066.8,0,7.22,8\n"
        "abc,1000,2,5,8.5\n"
    )
    response = client.post("/import", data=_csv_upload(csv_content), content_type="multipart/form-data")
    html = response.get_data(as_text=True)

    assert "Ligne 2 : La colonne « Age » doit être numérique." in html
    assert "Ligne 2 : La colonne « Account_Manager » doit valoir 0 ou 1." in html
    assert "Ligne 2 : La colonne « Num_Sites » doit être un nombre entier." in html


# --- T8/T9 : identifiant stable après tri, export d'une sélection précise --


def test_t8_t9_duplicate_names_stable_ids_and_exact_export(client):
    client.post(
        "/import", data=_csv_upload(CSV_THREE_CLIENTS_WITH_DUPLICATE_NAMES),
        content_type="multipart/form-data",
    )

    token = _session_token(client)
    records = app_module._IMPORT_STORE[token]["records"]
    by_id = {record["id"]: record for record in records}
    assert by_id[1]["Names"] == "Alice Martin" and by_id[1]["Company"] == "Harvey LLC"
    assert by_id[3]["Names"] == "Alice Martin" and by_id[3]["Company"] == "AutreCo"

    html = client.get("/resultats").get_data(as_text=True)
    ids_in_order = [int(value) for value in re.findall(r'name="selection" value="(\d+)"', html)]
    sorted_ids = [record["id"] for record in sorted(records, key=lambda r: r["score"], reverse=True)]
    assert ids_in_order == sorted_ids
    assert len(sorted_ids) == 3

    # Sélection de deux lignes non adjacentes dans l'affichage trié (premier et dernier rang).
    selected_ids = [sorted_ids[0], sorted_ids[-1]]
    assert abs(ids_in_order.index(selected_ids[0]) - ids_in_order.index(selected_ids[1])) > 1

    export_response = client.post("/export", data={"selection": [str(i) for i in selected_ids]})
    assert export_response.status_code == 200

    reader = csv.DictReader(io.StringIO(export_response.get_data(as_text=True)))
    exported = {int(row["id"]): row for row in reader}
    assert set(exported) == set(selected_ids)

    for client_id in selected_ids:
        expected = by_id[client_id]
        row = exported[client_id]
        assert row["Names"] == expected["Names"]
        assert row["Company"] == expected["Company"]
        for feature in config.FEATURE_COLUMNS:
            assert float(row[feature]) == pytest.approx(expected[feature])
        assert float(row["score"]) == pytest.approx(expected["score"])
        assert row["alerte"] == expected["alerte"]


# --- T10 : modèle absent ----------------------------------------------------


def test_t10_scoring_without_model_shows_clear_error(client):
    scoring.load_pipeline.cache_clear()
    backup_path = config.PIPELINE_PATH.with_suffix(".joblib.bak")
    config.PIPELINE_PATH.rename(backup_path)
    try:
        form_response = client.post("/", data=VALID_FORM)
        assert "Aucun modèle entraîné" in form_response.get_data(as_text=True)

        import_response = client.post(
            "/import", data=_csv_upload(CSV_ONE_CLIENT), content_type="multipart/form-data"
        )
        assert "Aucun modèle entraîné" in import_response.get_data(as_text=True)
    finally:
        backup_path.rename(config.PIPELINE_PATH)
        scoring.load_pipeline.cache_clear()


# --- T11 : isolation des sessions et des imports successifs ----------------


def test_t11a_two_independent_sessions_do_not_share_results(client):
    other_client = app_module.app.test_client()

    client.post("/import", data=_csv_upload(CSV_ONE_CLIENT), content_type="multipart/form-data")
    response = other_client.get("/resultats")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/import")


def test_t11b_new_import_replaces_previous_results_in_same_session(client):
    client.post("/import", data=_csv_upload(CSV_ONE_CLIENT), content_type="multipart/form-data")
    token = _session_token(client)
    assert len(app_module._IMPORT_STORE[token]["records"]) == 1

    csv_two_rows = (
        "Age,Total_Purchase,Account_Manager,Years,Num_Sites\n50,2000,1,3,4\n60,3000,0,4,6\n"
    )
    client.post("/import", data=_csv_upload(csv_two_rows), content_type="multipart/form-data")
    assert len(app_module._IMPORT_STORE[token]["records"]) == 2


def test_t11c_rejected_import_clears_previous_results_in_same_session(client):
    client.post("/import", data=_csv_upload(CSV_ONE_CLIENT), content_type="multipart/form-data")
    token = _session_token(client)
    assert token in app_module._IMPORT_STORE

    client.post("/import", data=_csv_upload(""), content_type="multipart/form-data")
    assert token not in app_module._IMPORT_STORE

    response = client.get("/resultats")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/import")


# --- Cohérence formulaire / CSV ---------------------------------------------


def test_same_values_give_same_score_via_form_and_csv(client):
    form_html = client.post("/", data=VALID_FORM).get_data(as_text=True)
    form_score = re.search(r"Score de risque : <strong>([\d.]+) %</strong>", form_html).group(1)

    csv_content = (
        "Age,Total_Purchase,Account_Manager,Years,Num_Sites\n"
        f"{VALID_FORM['Age']},{VALID_FORM['Total_Purchase']},{VALID_FORM['Account_Manager']},"
        f"{VALID_FORM['Years']},{VALID_FORM['Num_Sites']}\n"
    )
    client.post("/import", data=_csv_upload(csv_content), content_type="multipart/form-data")
    resultats_html = client.get("/resultats").get_data(as_text=True)
    csv_score = re.search(r">([\d.]+) %</td>", resultats_html).group(1)

    assert form_score == csv_score


# --- Seuil appliqué sur le score non arrondi --------------------------------


@pytest.mark.parametrize(
    "score, expected_alert, expected_display",
    [
        (0.5, "Risque élevé", "50.0 %"),
        (0.5004, "Risque élevé", "50.0 %"),
        (0.4996, "Risque faible", "50.0 %"),
        (0.4999999, "Risque faible", "50.0 %"),
    ],
)
def test_alert_threshold_uses_unrounded_score(client, monkeypatch, score, expected_alert, expected_display):
    monkeypatch.setattr(app_module, "load_pipeline", lambda: _FakePipeline(score))
    response = client.post("/", data=VALID_FORM)
    html = response.get_data(as_text=True)

    assert expected_display in html
    assert f"Alerte : <strong>{expected_alert}</strong>" in html


# --- Valeurs manquantes / non finies -----------------------------------------


def test_form_missing_and_non_finite_values_rejected(client):
    data = {"Age": "", "Total_Purchase": "nan", "Account_Manager": "1", "Years": "inf", "Num_Sites": "8"}
    html = client.post("/", data=data).get_data(as_text=True)

    assert "La colonne « Age » est manquante." in html
    assert "La colonne « Total_Purchase » doit être un nombre fini." in html
    assert "La colonne « Years » doit être un nombre fini." in html


def test_import_missing_and_non_finite_values_rejected(client):
    csv_content = "Age,Total_Purchase,Account_Manager,Years,Num_Sites\n,NaN,1,inf,8\n"
    html = client.post(
        "/import", data=_csv_upload(csv_content), content_type="multipart/form-data"
    ).get_data(as_text=True)

    assert "Ligne 1 : La colonne « Age » est manquante." in html
    assert "Ligne 1 : La colonne « Total_Purchase » est manquante." in html
    assert "Ligne 1 : La colonne « Years » doit être un nombre fini." in html


# --- Fichier CSV avec seulement les en-têtes --------------------------------


def test_import_headers_only_treated_as_empty_file(client):
    csv_content = "Age,Total_Purchase,Account_Manager,Years,Num_Sites\n"
    html = client.post(
        "/import", data=_csv_upload(csv_content), content_type="multipart/form-data"
    ).get_data(as_text=True)

    assert "Le fichier est vide." in html


# --- Démonstration avec le CSV historique complet (F-11) --------------------


def test_full_historical_csv_import_is_a_demo_and_ignores_churn(client):
    with open(config.DATA_PATH, "rb") as historical_file:
        response = client.post(
            "/import",
            data={"fichier": (historical_file, "customer_churn.csv")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Ce fichier contient une colonne « Churn » historique" in html

    token = _session_token(client)
    entry = app_module._IMPORT_STORE[token]
    assert entry["demo_import"] is True
    assert len(entry["records"]) == 900
    for record in entry["records"]:
        assert "Churn" not in record


# --- Preuve qu'aucun ré-entraînement n'est déclenché par les routes ---------


def test_routes_never_call_pipeline_fit(client, monkeypatch):
    def _fail_if_called(self, *args, **kwargs):
        raise AssertionError("fit() ne doit jamais être appelé depuis les routes Flask.")

    monkeypatch.setattr(LogisticRegression, "fit", _fail_if_called)

    form_response = client.post("/", data=VALID_FORM)
    assert "Score de risque" in form_response.get_data(as_text=True)

    import_response = client.post(
        "/import", data=_csv_upload(CSV_ONE_CLIENT), content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert "Risque" in import_response.get_data(as_text=True)
