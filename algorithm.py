import json
import unicodedata
from typing import Set, List, TextIO


# ---------------------------------------------------------
# FUNZIONI DI SUPPORTO
# ---------------------------------------------------------

def normalize_username(username: str) -> str:
    """
    Normalizza lo username:
    - lowercase
    - rimozione spazi invisibili / unicode strani
    - NFC (normalizzazione Unicode canonica)
    """
    if not isinstance(username, str):
        return ""

    username = username.strip().lower()
    username = unicodedata.normalize("NFC", username)

    
    return "".join(ch for ch in username if ch.isprintable())


def safe_extract_username_from_url(url: str) -> str:
    """
    Estrae in modo sicuro lo username dalla URL del profilo Instagram.
    Gestisce vari formati:
      • https://www.instagram.com/nome
      • https://www.instagram.com/nome/
      • https://www.instagram.com/_u/nome
      • https://instagram.com/nome
      • https://l.instagram.com/?u=xxxx (redirect)
    """
    if not isinstance(url, str) or not url.strip():
        return ""

    url = url.strip()

    
    if "l.instagram.com" in url and "u=" in url:
        
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            if "u" in qs:
                url = qs["u"][0]
        except Exception:
            pass

    
    url = url.rstrip("/")

    
    if "/_u/" in url:
        url = url.split("/_u/")[-1]
        return normalize_username(url)

    
    last = url.split("/")[-1]
    return normalize_username(last)


def safe_read_json(file_stream: TextIO):
    """
    Carica JSON senza far crashare l'algoritmo.
    Ritorna [] o {} in caso di errore.
    """
    try:
        return json.load(file_stream)
    except Exception:
        return {}  


# ---------------------------------------------------------
# PARSING FOLLOWERS
# ---------------------------------------------------------

def load_followers(file_stream: TextIO) -> Set[str]:
    """
    Carica l'insieme degli username dei follower dal JSON esportato.
    È estremamente robusto: ignora record rotti senza mai crashare.
    """
    data = safe_read_json(file_stream)

    followers: Set[str] = set()

    if not isinstance(data, list):
        return followers

    for item in data:
        if not isinstance(item, dict):
            continue

        sld = item.get("string_list_data")
        if not isinstance(sld, list) or not sld:
            continue

        first = sld[0] if isinstance(sld[0], dict) else None
        if not first:
            continue

        url = first.get("href")
        username = safe_extract_username_from_url(url)

        if username:
            followers.add(username)

    return followers


# ---------------------------------------------------------
# PARSING FOLLOWING
# ---------------------------------------------------------

def load_following(file_stream: TextIO) -> List[str]:
    """
    Carica la lista degli username che TU segui dal JSON esportato.
    Anche qui, parsing ultra-robusto.
    """
    data = safe_read_json(file_stream)

    following: List[str] = []

    entries = data.get("relationships_following")
    if not isinstance(entries, list):
        return following

    for item in entries:
        if not isinstance(item, dict):
            continue

        sld = item.get("string_list_data")
        if not isinstance(sld, list) or not sld:
            continue

        first = sld[0] if isinstance(sld[0], dict) else None
        if not first:
            continue

        url = first.get("href")
        username = safe_extract_username_from_url(url)

        if username:
            following.append(username)

    return following


# ---------------------------------------------------------
# ANALISI
# ---------------------------------------------------------

def analyze(followers_file: TextIO, following_file: TextIO) -> List[str]:
    """
    Restituisce la lista ordinata degli utenti che TU segui
    ma che non ti seguono più (no follow-back).

    Logica:
      - followers   = insieme dei profili che ti seguono
      - following   = insieme dei profili che segui tu
      - risultato   = following - followers
      - ordinato alfabeticamente
    """
    followers = load_followers(followers_file)       # set
    following = set(load_following(following_file))  # set

    non_seguono = sorted(following - followers)

    return non_seguono
