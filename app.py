"""Application Flask d'aide au rappel commercial (F-01 à F-11).

Les scores d'un import CSV sont conservés côté serveur (mémoire du
processus), associés à un jeton de session propre à chaque utilisateur —
jamais dans une variable globale partagée entre utilisateurs, ni dans un
cookie volumineux. Stockage suffisant pour cette démonstration mono-processus
(non persistant, perdu au redémarrage).
"""

import io
import secrets
import uuid

import pandas as pd
from flask import Flask, Response, redirect, render_template, request, session, url_for

from config import FEATURE_COLUMNS, RISK_THRESHOLD, TARGET_COLUMN
from scoring import ModelNotFoundError, alert_label, load_pipeline, score_record
from validation import validate_dataframe, validate_record

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

OPTIONAL_COLUMNS = ["Names", "Company"]
EXPORT_COLUMNS = ["id", "Names", "Company", *FEATURE_COLUMNS, "score", "alerte"]

# Résultats d'import en cours, indexés par jeton de session (démo mono-processus).
# Chaque entrée : {"records": [...], "demo_import": bool, "version": str}.
_IMPORT_STORE: dict[str, dict] = {}


@app.context_processor
def inject_threshold():
    return {"threshold": RISK_THRESHOLD}


def _session_token() -> str:
    token = session.get("import_token")
    if token is None:
        token = uuid.uuid4().hex
        session["import_token"] = token
    return token


@app.route("/", methods=["GET", "POST"])
def formulaire():
    result = None
    errors = []
    form_values = {column: request.form.get(column, "") for column in FEATURE_COLUMNS}

    if request.method == "POST":
        values, errors = validate_record(request.form)
        if not errors:
            try:
                pipeline = load_pipeline()
            except ModelNotFoundError as exc:
                errors = [str(exc)]
            else:
                score = score_record(pipeline, values)
                result = {"score": score, "alerte": alert_label(score)}

    return render_template(
        "form.html",
        form_values=form_values,
        result=result,
        errors=errors,
    )


@app.route("/import", methods=["GET", "POST"])
def import_csv():
    errors = []

    if request.method == "POST":
        token = _session_token()
        uploaded_file = request.files.get("fichier")
        if uploaded_file is None or uploaded_file.filename == "":
            errors = ["Veuillez choisir un fichier CSV à importer."]
        else:
            try:
                df = pd.read_csv(uploaded_file)
            except pd.errors.EmptyDataError:
                errors = ["Le fichier est vide."]
            except (pd.errors.ParserError, UnicodeDecodeError, ValueError):
                errors = ["Le fichier n'est pas un CSV valide."]
            else:
                errors = validate_dataframe(df)

        if not errors:
            try:
                pipeline = load_pipeline()
            except ModelNotFoundError as exc:
                errors = [str(exc)]

        if errors:
            # Un import rejeté invalide tout résultat précédent de cette session :
            # on ne doit jamais pouvoir consulter ou exporter une ancienne sélection.
            _IMPORT_STORE.pop(token, None)
            return render_template("import.html", errors=errors)

        demo_import = TARGET_COLUMN in df.columns
        records = []
        for row_position, (_, row) in enumerate(df.iterrows(), start=1):
            values, _ = validate_record(row)
            score = score_record(pipeline, values)
            record = {"id": row_position, **values}
            for optional_column in OPTIONAL_COLUMNS:
                record[optional_column] = (
                    str(row[optional_column]) if optional_column in df.columns else None
                )
            record["score"] = score
            record["alerte"] = alert_label(score)
            records.append(record)

        _IMPORT_STORE[token] = {
            "records": records,
            "demo_import": demo_import,
            # Version unique par import : empêche qu'une sélection affichée
            # avant un nouvel import n'exporte silencieusement les clients
            # du nouvel import (les identifiants sont réutilisés à chaque import).
            "version": uuid.uuid4().hex,
        }
        return redirect(url_for("resultats"))

    return render_template("import.html", errors=errors)


def _render_resultats(entry, errors=None):
    records = entry["records"]
    records_tries = sorted(records, key=lambda r: r["score"], reverse=True)
    return render_template(
        "resultats.html",
        records=records_tries,
        has_names=any(r["Names"] for r in records),
        has_company=any(r["Company"] for r in records),
        demo_import=entry["demo_import"],
        version=entry["version"],
        errors=errors or [],
    )


@app.route("/resultats")
def resultats():
    entry = _IMPORT_STORE.get(session.get("import_token"))
    if not entry:
        return redirect(url_for("import_csv"))

    return _render_resultats(entry)


@app.route("/export", methods=["POST"])
def export_selection():
    entry = _IMPORT_STORE.get(session.get("import_token"))
    if not entry:
        return redirect(url_for("import_csv"))

    submitted_version = request.form.get("version")
    if not submitted_version or submitted_version != entry["version"]:
        return _render_resultats(
            entry,
            errors=[
                "Cette sélection provient d'un import précédent et n'est plus "
                "valide : veuillez sélectionner à nouveau les clients dans la "
                "liste actuelle avant d'exporter."
            ],
        )

    records = entry["records"]
    selected_ids = {int(value) for value in request.form.getlist("selection")}
    selected_records = [record for record in records if record["id"] in selected_ids]

    if not selected_records:
        return redirect(url_for("resultats"))

    export_df = pd.DataFrame(selected_records)[EXPORT_COLUMNS]
    buffer = io.StringIO()
    export_df.to_csv(buffer, index=False)

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients_a_rappeler.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
