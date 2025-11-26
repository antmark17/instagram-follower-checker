# 📸 Instagram Follower Checker

**Analizza chi non ti segue più usando i file ufficiali esportati da
Instagram.**\
Sicuro, affidabile e compatibile con i nuovi formati JSON Meta
(2024--2025+).

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-green) ![License:
MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

------------------------------------------------------------------------

## ✨ Caratteristiche

-   Analisi dei profili tramite file esportati ufficialmente da
    Instagram
-   Supporto ai **nuovi formati JSON Meta** (2024--2025+)
-   Algoritmo intelligente per il confronto *followers vs following*
-   Interfaccia moderna con dark/light mode
-   Sicuro:
    -   Validazione avanzata dei file JSON
    -   Protezione CSRF
    -   Rate limiting
    -   Anti-corruzione file e controllo MIME
    -   Secret key sicura (via `.env`)
    -   Nessun dato salvato su disco (elaborazione solo in RAM)
    -   Header anti-cache globali per maggiore privacy
-   Drag & Drop migliorato:
    -   Anti-reset del file già caricato
    -   Blocco caricamento multiplo
-   Download del risultato tramite **POST** (più sicuro di GET)
-   Risultato esportato in `Result.txt`

------------------------------------------------------------------------

## 📦 Requisiti

-   Python 3.9 o superiore\
-   pip

------------------------------------------------------------------------

## 🔧 Installazione locale

Clona la repository:

``` bash
git clone https://github.com/tuo_username/instagram-follower-checker.git
cd instagram-follower-checker
```

Installa le dipendenze:

``` bash
pip install -r requirements.txt
```

Crea un file `.env` con:

    SECRET_KEY="tua-secret-key-sicura"

Avvia l'app:

``` bash
python app.py
```

L'app sarà disponibile su:

    http://127.0.0.1:5000

------------------------------------------------------------------------

## 📂 Struttura del progetto

    📁 PY
     ├── app.py
     ├── algorithm.py
     ├── static/style.css
     ├── templates/
     │   ├── upload.html
     │   ├── result.html
     │   └── info.html
     ├── .env
     ├── .gitignore
     ├── LICENSE
     ├── Procfile
     └── README.md

------------------------------------------------------------------------

## 🔐 Sicurezza

### ✔ CSRF Protection

Ogni form contiene un token sicuro per prevenire attacchi cross-site.

### ✔ Rate Limiting

-   `/analizza` → max 10 richieste/minuto\
-   `/download` → max 30 richieste/minuto

### ✔ Validazione avanzata dei file

-   Controllo MIME del file\
-   JSON valido\
-   Rilevamento null bytes (`