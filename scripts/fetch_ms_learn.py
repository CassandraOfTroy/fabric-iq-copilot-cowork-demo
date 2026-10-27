"""Fetch Microsoft Learn pages into references/ms-learn/ as markdown (traceability cache).

Usage (from repo root):
    python scripts/fetch_ms_learn.py references/ms-learn/_sources.csv

The CSV has two columns: slug,url. Each page is saved to references/ms-learn/<slug>.md with the
source URL and fetch date at the top. Only the article body (<main>) is kept.
Requires: requests, beautifulsoup4, markdownify (see requirements.txt).
"""
from __future__ import annotations

import csv
import datetime as dt
import pathlib
import re
import sys

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as to_md

HEADERS = {"User-Agent": "Mozilla/5.0 (fabric-iq-copilot-cowork-demo reference cache)"}


def fetch(url: str) -> tuple[str, str]:
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    if url.endswith(".md") or resp.headers.get("Content-Type", "").startswith("text/plain"):
        first = next((ln for ln in resp.text.splitlines() if ln.startswith("# ")), url)
        return first.lstrip("# ").strip(), resp.text.strip()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = (soup.find("h1") or soup.find("title")).get_text(strip=True)
    main = soup.find("main") or soup.find("div", class_="content") or soup.body
    for tag in main.select(
        "nav, script, style, .feedback-section, #ms--inline-notifications, "
        ".display-none-print, [data-bi-name='feedback'], .action-container, #article-header"
    ):
        tag.decompose()
    md = to_md(str(main), heading_style="ATX", bullets="-")
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return title, md


def main() -> int:
    index = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "references/ms-learn/_sources.csv")
    out_dir = index.parent
    today = dt.date.today().isoformat()
    failures = 0
    with index.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            slug, url = row["slug"].strip(), row["url"].strip()
            try:
                title, body = fetch(url)
                target = out_dir / f"{slug}.md"
                target.write_text(
                    f"Source: {url}\nFetched: {today}\n\n# {title}\n\n{body}\n", encoding="utf-8"
                )
                print(f"OK   {slug:55s} {len(body):>7,d} chars")
            except Exception as exc:  # noqa: BLE001 - report and continue
                failures += 1
                print(f"FAIL {slug:55s} {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
