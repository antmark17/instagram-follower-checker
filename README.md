# 📸 Instagram Follower Checker
**Analizza chi non ti segue più usando SOLO i file ufficiali esportati da Instagram.**  
Totalmente privacy-friendly, nessun dato viene inviato o salvato su server.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)


---

## ✨ Caratteristiche

- Analisi totalmente locale: nessun dato inviato online
- Algoritmo intelligente che confronta followers vs following
- Interfaccia moderna (dark/light mode) stile Instagram
- Sicuro:
  - Validazione JSON avanzata
  - CSRF Protection
  - Rate limiting
  - Anti-corruzione file
  - Secret key sicura
- Download del risultato in `Result.txt`

---

## 📦 Requisiti

- Python 3.9 o superiore
- pip

---

## 🔧 Installazione locale

Clona la repo:

```bash
git clone https://github.com/tuo_username/instagram-follower-checker.git
cd instagram-follower-checker
```

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

Crea un file `.env` con:

```
SECRET_KEY= "latuasecretkey"
```

Avvia l’app:

```bash
python app.py
```

L’app sarà disponibile su:

```
http://127.0.0.1:5000
```

---

## 📂 Struttura del progetto

```
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
```

---

## 🔐 Sicurezza

### ✔ CSRF Protection  
Ogni form contiene un token verificato lato server.

### ✔ Rate Limiting  
- `/analizza` → max 10 richieste/minuto  
- `/download` → max 30 richieste/minuto

### ✔ Validazione avanzata dei file  
- JSON valido  
- MIME controllato  
- No file binari rinominati  
- No null bytes  
- Controllo struttura Instagram autentica

### ✔ Nessun dato salvato  
Tutto è processato in RAM.

---


## 🔮 Roadmap futura

- Supporto per più file followers
- Modalità confronto cronologico
- Supporto export Instagram HTML
- Modalità desktop app

---

## 📝 License  
MIT License – vedi il file LICENSE


---

## 👤 Autore

**Antonio Marco Vanacore**  
2025 – Tutti i diritti riservati
