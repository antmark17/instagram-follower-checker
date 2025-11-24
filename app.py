from flask import Flask, render_template, request, send_file, session, flash, redirect
import json
import io
import algorithm
import os
from dotenv import load_dotenv
import secrets
from werkzeug.utils import secure_filename


from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__)

# -------------------------------
# CONFIG DI BASE
# -------------------------------


app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# SECRET KEY
secret = os.getenv("SECRET_KEY")
if not secret:
    secret = secrets.token_hex(32)
    print("⚠ Nessuna SECRET_KEY trovata nel .env → generata automaticamente!")
app.secret_key = secret


app.config["SESSION_COOKIE_HTTPONLY"] = True


# -------------------------------
# CSRF PROTECTION
# -------------------------------
csrf = CSRFProtect(app)

# -------------------------------
# RATE LIMITING
# -------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[] 
)

# -------------------------------
# VALIDAZIONI FILE
# -------------------------------

def validate_followers_structure(file_stream):
    """Valida il file dei follower (followers_1.json)."""
    try:
        data = json.load(file_stream)
    except json.JSONDecodeError:
        return False, (
            "followers_1.json non è un file JSON valido. "
            "Assicurati di caricare il file originale ottenuto dall’esportazione di Instagram."
        )
    except Exception:
        return False, (
            "Si è verificato un errore durante la lettura di followers_1.json."
        )

    if not isinstance(data, list) or not data:
        return False, (
            "followers_1.json sembra vuoto o con una struttura non valida. "
            "Potrebbe non provenire dall’esportazione ufficiale di Instagram."
        )

    for item in data:
        if not isinstance(item, dict):
            continue

        sld = item.get("string_list_data")
        if not isinstance(sld, list) or not sld:
            continue

        first = sld[0]
        if not isinstance(first, dict):
            continue

        href = first.get("href")
        if isinstance(href, str) and href.strip():
            return True, ""

    return (
        False,
        "followers_1.json non contiene le informazioni necessarie per identificare i profili. "
        "Verifica di aver caricato il file originale presente nella cartella 'connections' "
        "dell’esportazione ufficiale di Instagram."
    )


def validate_following_structure(file_stream):
    """Valida il file dei profili che segui (following.json)."""
    try:
        data = json.load(file_stream)
    except json.JSONDecodeError:
        return False, (
            "following.json non è un file JSON valido. "
            "Assicurati di caricare il file originale ottenuto dall’esportazione di Instagram."
        )
    except Exception:
        return False, (
            "Si è verificato un errore durante la lettura di following.json."
        )

    if not isinstance(data, dict):
        return False, (
            "following.json ha una struttura non valida. "
            "Il file dovrebbe contenere un oggetto JSON (dict) con la sezione "
            "'relationships_following'."
        )

    rf = data.get("relationships_following")
    if not isinstance(rf, list) or not rf:
        return False, (
            "La sezione 'relationships_following' risulta vuota o non formattata correttamente. "
            "Verifica di aver caricato il file originale presente nella cartella 'connections' "
            "dell’esportazione ufficiale di Instagram."
        )

    for item in rf:
        if not isinstance(item, dict):
            continue

        sld = item.get("string_list_data")
        if not isinstance(sld, list) or not sld:
            continue

        first = sld[0]
        if not isinstance(first, dict):
            continue

        href = first.get("href")
        if isinstance(href, str) and href.strip():
            return True, ""

    return (
        False,
        "following.json non contiene dati validi per identificare gli utenti seguiti. "
        "Assicurati di caricare il file originale presente nella cartella 'connections' "
        "dell’esportazione ufficiale di Instagram."
    )

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/analizza", methods=["POST"])
@limiter.limit("10 per minuto")  
def analizza():

    if "followers" not in request.files or "following" not in request.files:
        flash("Devi caricare entrambi i file richiesti (followers e following).")
        return redirect("/")

    followers_file = request.files["followers"]
    following_file = request.files["following"]

    if followers_file.filename == "":
        flash("Devi caricare il file JSON dei follower (es. followers_1.json).")
        return redirect("/")

    if following_file.filename == "":
        flash("Devi caricare il file JSON dei profili che segui (es. following.json).")
        return redirect("/")

    followers_filename = secure_filename(followers_file.filename)
    following_filename = secure_filename(following_file.filename)

    if not followers_filename.lower().endswith(".json"):
        flash("Il file dei follower deve essere in formato .json.")
        return redirect("/")

    if not following_filename.lower().endswith(".json"):
        flash("Il file dei profili seguiti deve essere in formato .json.")
        return redirect("/")

    if followers_file.mimetype not in ["application/json", "text/plain"]:
        flash("Il file dei follower non è riconosciuto come JSON valido.")
        return redirect("/")

    if following_file.mimetype not in ["application/json", "text/plain"]:
        flash("Il file dei profili seguiti non è riconosciuto come JSON valido.")
        return redirect("/")

    followers_bytes = followers_file.read()
    following_bytes = following_file.read()

    if not followers_bytes:
        flash("Il file dei follower risulta vuoto.")
        return redirect("/")

    if not following_bytes:
        flash("Il file dei profili che segui risulta vuoto.")
        return redirect("/")

    if b"\x00" in followers_bytes[:200]:
        flash("Il file dei follower sembra corrotto o non un vero JSON.")
        return redirect("/")

    if b"\x00" in following_bytes[:200]:
        flash("Il file dei profili seguiti sembra corrotto o non un vero JSON.")
        return redirect("/")

    ok, msg = validate_followers_structure(io.BytesIO(followers_bytes))
    if not ok:
        flash(msg)
        return redirect("/")

    ok, msg = validate_following_structure(io.BytesIO(following_bytes))
    if not ok:
        flash(msg)
        return redirect("/")

    utenti = algorithm.analyze(
        io.BytesIO(followers_bytes),
        io.BytesIO(following_bytes)
    )

    
    result_text = "\n".join(utenti)
    session["result_text"] = result_text

    return render_template("result.html", utenti=utenti)


@app.route("/download")
@limiter.limit("30 per minuto")  
def download():
    """Crea il file Result.txt in RAM e lo invia senza salvarlo sul disco."""
    result_text = session.get("result_text", "")

    buffer = io.BytesIO(result_text.encode("utf-8"))
    buffer.seek(0)

    filename = f"Result_{secrets.token_hex(4)}.txt"

    response = send_file(
        buffer,
        mimetype="text/plain",
        as_attachment=True,
        download_name=filename
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@app.route("/info")
def info():
    return render_template("info.html")


if __name__ == "__main__":
    app.run(debug=True)
