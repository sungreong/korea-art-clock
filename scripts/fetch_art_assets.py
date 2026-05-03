#!/usr/bin/env python3
"""Download public-domain artwork assets for Korea Art Clock.

The script uses open-access museum APIs to find public-domain artworks,
downloads one image at a time, and writes a JavaScript manifest that can be
loaded from a static GitHub Pages site.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:  # pragma: no cover - the script can still fail clearly.
    Image = None  # type: ignore[assignment]


API_ROOT = "https://api.artic.edu/api/v1"
IIIF_ROOT = "https://www.artic.edu/iiif/2"
MET_ROOT = "https://collectionapi.metmuseum.org/public/collection/v1"
CMA_ROOT = "https://openaccess-api.clevelandart.org/api"
DEFAULT_TERMS = [
    "landscape",
    "nature",
    "flowers",
    "garden",
    "seascape",
    "birds",
    "animals",
    "still life",
    "impressionism",
    "painting",
    "mountain",
    "water",
]
FIELDS = "id,title,artist_display,date_display,image_id,is_public_domain"
USER_AGENT = "Mozilla/5.0 KoreaArtClock/1.0"
AIC_USER_AGENT = "korea-art-clock asset fetcher (public GitHub Pages project)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100, help="number of images to keep")
    parser.add_argument("--width", type=int, default=843, help="download width in pixels")
    parser.add_argument("--delay", type=float, default=1.0, help="delay between image downloads")
    parser.add_argument("--quality", type=int, default=84, help="JPEG output quality")
    parser.add_argument("--source", choices=["auto", "cma", "met", "aic"], default="auto")
    parser.add_argument("--out-dir", default="assets/artworks", help="image output directory")
    parser.add_argument("--manifest", default="assets/artworks.js", help="JS manifest path")
    args = parser.parse_args()

    if args.count < 1:
        raise SystemExit("--count must be at least 1")
    if Image is None:
        raise SystemExit("Pillow is required. Install it with: python -m pip install pillow")

    root = Path.cwd()
    out_dir = root / args.out_dir
    temp_out_dir = out_dir.with_name(out_dir.name + ".tmp")
    manifest_path = root / args.manifest
    if temp_out_dir.exists():
        shutil.rmtree(temp_out_dir)
    temp_out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    candidate_count = max(args.count * 2, args.count + 20)
    artworks = collect_candidates(args.source, candidate_count)
    if len(artworks) < candidate_count:
        print(f"warning: found only {len(artworks)} candidate artworks", file=sys.stderr)

    selected: list[dict[str, Any]] = []
    for artwork in artworks:
        if len(selected) >= args.count:
            break
        index = len(selected) + 1
        filename = f"art-{index:03d}.jpg"
        output_path = temp_out_dir / filename
        image_url = artwork.get("download_url") or iiif_url(str(artwork["image_id"]), args.width)
        print(f"[{index:03d}/{args.count:03d}] {artwork.get('title', 'Untitled')}")
        try:
            image_info = download_and_optimize(image_url, output_path, args.width, args.quality)
        except Exception as exc:
            print(f"  skipped: {exc}", file=sys.stderr)
            continue
        selected.append(
            {
                "src": f"assets/artworks/{filename}",
                "title": clean_text(artwork.get("title") or "Untitled"),
                "artist": clean_text(
                    artwork.get("artist")
                    or artwork.get("artist_display")
                    or "Unknown artist"
                ),
                "date": clean_text(artwork.get("date") or artwork.get("date_display") or ""),
                "source": clean_text(artwork.get("source") or "Art Institute of Chicago"),
                "sourceUrl": clean_text(
                    artwork.get("source_url") or f"https://www.artic.edu/artworks/{artwork['id']}"
                ),
                "publicDomain": True,
                "license": clean_text(artwork.get("license") or "CC0"),
                "width": image_info["width"],
                "height": image_info["height"],
                "bytes": image_info["bytes"],
            }
        )
        if len(selected) < args.count:
            time.sleep(args.delay)

    if len(selected) < args.count:
        shutil.rmtree(temp_out_dir, ignore_errors=True)
        raise SystemExit(f"downloaded only {len(selected)} images; try a larger search set")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    temp_out_dir.replace(out_dir)
    write_manifest(manifest_path, selected)
    print(f"Wrote {len(selected)} images and {manifest_path}")
    return 0


def collect_candidates(source: str, count: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    sources = ["cma", "met", "aic"] if source == "auto" else [source]
    for source_name in sources:
        if source_name == "cma":
            candidates.extend(collect_cma_artworks(count))
        elif source_name == "met":
            candidates.extend(collect_met_artworks(count))
        elif source_name == "aic":
            candidates.extend(collect_aic_artworks(count))
        if len(candidates) >= count:
            break
    return candidates


def collect_cma_artworks(count: int) -> list[dict[str, Any]]:
    seen: set[str] = set()
    artworks: list[dict[str, Any]] = []
    per_term_limit = max(12, min(40, count // len(DEFAULT_TERMS) + 8))

    for term in DEFAULT_TERMS:
        if len(artworks) >= count:
            break
        for item in search_cma_artworks(term, per_term_limit):
            if len(artworks) >= count:
                break
            accession = str(item.get("accession_number") or item.get("id") or "")
            images = item.get("images") if isinstance(item.get("images"), dict) else {}
            web_image = images.get("web") if isinstance(images.get("web"), dict) else {}
            image_url = web_image.get("url")
            if not accession or accession in seen or not image_url:
                continue
            if item.get("share_license_status") != "CC0":
                continue
            seen.add(accession)
            creators = item.get("creators") if isinstance(item.get("creators"), list) else []
            artist = "Unknown artist"
            if creators and isinstance(creators[0], dict) and creators[0].get("description"):
                artist = str(creators[0]["description"])
            artworks.append(
                {
                    "id": accession,
                    "title": item.get("title") or "Untitled",
                    "artist": artist,
                    "date": item.get("creation_date") or item.get("date_text") or "",
                    "download_url": image_url,
                    "source": "Cleveland Museum of Art",
                    "source_url": item.get("url") or f"https://www.clevelandart.org/art/{accession}",
                    "publicDomain": True,
                    "license": "CC0",
                }
            )

    return artworks


def search_cma_artworks(term: str, limit: int) -> list[dict[str, Any]]:
    params = {
        "q": term,
        "cc0": "",
        "has_image": "1",
        "limit": str(min(100, max(10, limit))),
    }
    url = f"{CMA_ROOT}/artworks/?{urllib.parse.urlencode(params)}"
    data = request_json(url)
    items = data.get("data") if isinstance(data, dict) else None
    return items if isinstance(items, list) else []


def collect_aic_artworks(count: int) -> list[dict[str, Any]]:
    seen: set[int] = set()
    artworks: list[dict[str, Any]] = []
    page_by_term = {term: 1 for term in DEFAULT_TERMS}

    while len(artworks) < count:
        progress = False
        for term in DEFAULT_TERMS:
            if len(artworks) >= count:
                break
            page = page_by_term[term]
            page_by_term[term] += 1
            for item in search_artworks(term, page):
                artwork_id = item.get("id")
                image_id = item.get("image_id")
                if not artwork_id or not image_id or artwork_id in seen:
                    continue
                if item.get("is_public_domain") is False:
                    continue
                seen.add(int(artwork_id))
                item["source"] = "Art Institute of Chicago"
                item["source_url"] = f"https://www.artic.edu/artworks/{artwork_id}"
                artworks.append(item)
                progress = True
                if len(artworks) >= count:
                    break
        if not progress:
            break

    return artworks


def collect_met_artworks(count: int) -> list[dict[str, Any]]:
    seen: set[int] = set()
    artworks: list[dict[str, Any]] = []

    for term in DEFAULT_TERMS:
        if len(artworks) >= count:
            break
        for object_id in search_met_objects(term):
            if len(artworks) >= count:
                break
            if object_id in seen:
                continue
            seen.add(object_id)
            item = get_met_object(object_id)
            if not item or not item.get("isPublicDomain"):
                continue
            image_url = item.get("primaryImageSmall") or item.get("primaryImage")
            if not image_url:
                continue
            artworks.append(
                {
                    "id": object_id,
                    "title": item.get("title") or "Untitled",
                    "artist": item.get("artistDisplayName") or "Unknown artist",
                    "date": item.get("objectDate") or "",
                    "download_url": image_url,
                    "source": "The Metropolitan Museum of Art",
                    "source_url": item.get("objectURL") or f"https://www.metmuseum.org/art/collection/search/{object_id}",
                    "publicDomain": True,
                }
            )

    return artworks


def search_met_objects(term: str) -> list[int]:
    params = {
        "hasImages": "true",
        "isPublicDomain": "true",
        "q": term,
    }
    url = f"{MET_ROOT}/search?{urllib.parse.urlencode(params)}"
    data = request_json(url)
    ids = data.get("objectIDs") if isinstance(data, dict) else None
    if not isinstance(ids, list):
        return []
    return [int(object_id) for object_id in ids if isinstance(object_id, int)]


def get_met_object(object_id: int) -> dict[str, Any] | None:
    try:
        data = request_json(f"{MET_ROOT}/objects/{object_id}")
    except Exception as exc:
        print(f"  skipped Met object {object_id}: {exc}", file=sys.stderr)
        return None
    return data if isinstance(data, dict) else None


def search_artworks(term: str, page: int) -> list[dict[str, Any]]:
    params = {
        "q": term,
        "query[term][is_public_domain]": "true",
        "fields": FIELDS,
        "limit": "100",
        "page": str(page),
    }
    url = f"{API_ROOT}/artworks/search?{urllib.parse.urlencode(params)}"
    data = request_json(url)
    items = data.get("data") if isinstance(data, dict) else None
    return items if isinstance(items, list) else []


def request_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "AIC-User-Agent": AIC_USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_and_optimize(url: str, output_path: Path, width: int, quality: int) -> dict[str, int]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "AIC-User-Agent": AIC_USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"failed to download {url}: HTTP {exc.code}") from exc

    with Image.open(BytesIO(raw)) as image:
        image = image.convert("RGB")
        if image.width > width:
            height = max(1, round(image.height * (width / image.width)))
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        image.save(output_path, format="JPEG", quality=quality, optimize=True, progressive=True)
        return {
            "width": image.width,
            "height": image.height,
            "bytes": output_path.stat().st_size,
        }


def iiif_url(image_id: str, width: int) -> str:
    return f"{IIIF_ROOT}/{urllib.parse.quote(image_id)}/full/{width},/0/default.jpg"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def write_manifest(path: Path, artworks: list[dict[str, Any]]) -> None:
    manifest = {
        "version": 1,
        "generatedAt": date.today().isoformat(),
        "items": artworks,
    }
    payload = json.dumps(manifest, ensure_ascii=False, indent=2)
    path.write_text(
        "window.KOREA_ART_CLOCK_ARTWORKS = " + payload + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
