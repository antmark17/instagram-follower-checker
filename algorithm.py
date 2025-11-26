import json
import unicodedata
from typing import Set, List, TextIO

def normalize_username(username: str) -> str:
    if not isinstance(username, str):
        return ""

    username = username.strip().lower()
    username = unicodedata.normalize("NFC", username)

    return "".join(ch for ch in username if ch.isprintable())


def safe_extract_username_from_url(url: str) -> str:
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
    try:
        return json.load(file_stream)
    except Exception:
        return {}  




def extract_href(data):
    """Ricerca ricorsiva di un campo href all'interno del JSON Instagram."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "href" and isinstance(value, str) and value.strip():
                return value
            found = extract_href(value)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = extract_href(item)
            if found:
                return found
    return None




def load_followers(file_stream: TextIO) -> Set[str]:
    data = safe_read_json(file_stream)
    followers: Set[str] = set()

    if not isinstance(data, list):
        return followers

    for item in data:
        href = extract_href(item)
        if not href:
            continue

        username = safe_extract_username_from_url(href)
        if username:
            followers.add(username)

    return followers



def load_following(file_stream: TextIO) -> List[str]:
    data = safe_read_json(file_stream)
    following: List[str] = []


    results = []

    def collect_hrefs(data, results):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "href" and isinstance(value, str):
                    results.append(value)
                collect_hrefs(value, results)
        elif isinstance(data, list):
            for item in data:
                collect_hrefs(item, results)

    collect_hrefs(data, results)

    for url in results:
        username = safe_extract_username_from_url(url)
        if username:
            following.append(username)

    return following


def analyze(followers_file: TextIO, following_file: TextIO) -> List[str]:
    followers = load_followers(followers_file)       
    following = set(load_following(following_file))  

    non_seguono = sorted(following - followers)
    return non_seguono
