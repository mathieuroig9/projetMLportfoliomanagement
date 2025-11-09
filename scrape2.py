# scrape2.py
import os
import re
import time
from typing import Iterable, Tuple

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from tools import gen, get_txt_file

BASE_URL = "https://www.minneapolisfed.org/beige-book-reports/"
USER_AGENT = "Mozilla/5.0 (compatible; BeigeBookScraper/1.0)"

# --- parser helper -----------------------------------------------------------
def _bs_parser_name() -> str:
    # utilise html5lib si installé, sinon html.parser
    try:
        import html5lib  # noqa: F401
        return "html5lib"
    except Exception:
        return "html.parser"

PARSER = _bs_parser_name()

# --- HTTP session avec retries ----------------------------------------------
def make_session() -> Session:
    s = Session()
    s.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=3,
        backoff_factor=0.7,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

# --- extraction du texte -----------------------------------------------------
def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, PARSER)
    div = (
        soup.find("div", class_="col-sm-12 col-lg-8 offset-lg-1")
        or soup.find("main")
        or soup.find("article")
        or soup.body
    )
    if not div:
        raise ValueError("content container not found")
    raw = re.sub(r"\s*\n\s*", "\n", div.get_text("\n", strip=True)).strip()
    lines = [l for l in raw.splitlines() if l.strip()]
    return "\n".join(lines[3:]) if len(lines) > 3 else "\n".join(lines)

def fetch_url(session: Session, url: str, timeout: int = 20) -> str:
    r = session.get(url, timeout=timeout)
    if r.status_code == 404:
        raise ValueError("not found")
    r.raise_for_status()
    return extract_text(r.text)

def fetch_national(session: Session, year: int, month: int) -> str:
    for slug in ("su", "national-summary"):
        url = f"{BASE_URL}{year}/{year}-{month:02d}-{slug}"
        r = session.get(url, timeout=20)
        if r.status_code == 200:
            return extract_text(r.text)
        if r.status_code in (301, 302, 404):
            continue
        r.raise_for_status()
    raise ValueError("national summary not found")

def gen_range(start_year: int, end_year: int) -> Iterable[Tuple[int, int, str]]:
    for y, m, r in gen(skip=False):
        if start_year <= y <= end_year:
            yield y, m, r

def scrape_all(start_year: int = 1970, end_year: int = 2025, polite_sleep: float = 0.0):
    os.makedirs("out/csv", exist_ok=True)
    session = make_session()
    missing_path = "out/csv/missing.csv"
    if not os.path.exists(missing_path):
        with open(missing_path, "w", encoding="utf-8") as f:
            f.write("year,month,region\n")

    with open(missing_path, "a", encoding="utf-8") as miss:
        for year, month, region in gen_range(start_year, end_year):
            filename = get_txt_file((year, month, region))
            if os.path.exists(filename):
                print(f"{year} {month:02d} {region} skip")
                continue

            print(f"{year} {month:02d} {region}", end=" ")
            try:
                if region == "su":
                    txt = fetch_national(session, year, month)
                else:
                    slug = region  # districts: slug identique au code (at, bo, ..., sl)
                    url = f"{BASE_URL}{year}/{year}-{month:02d}-{slug}"
                    txt = fetch_url(session, url)

                # écriture
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(txt)
                print("y")
                if polite_sleep:
                    time.sleep(polite_sleep)

            except Exception as e:
                print(f"n ({e})")
                miss.write(f"{year},{month:02d},{region}\n")

    print("\n Scraping terminé.")

if __name__ == "__main__":
    scrape_all(1970, 2025, polite_sleep=0.0)
