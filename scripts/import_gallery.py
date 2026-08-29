#!/usr/bin/env python3
"""Import unique photos from Shutterstock_Categories into the Hugo gallery."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SRC = Path("/Volumes/photo/Best/Shutterstock_Categories")
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets/images/gallery"
CONTENT = ROOT / "content/fotografiya"
STATE = ROOT / "scripts/.gallery-import-state.json"
MAX_EDGE = 2000
JPEG_Q = 82
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

ALBUMS = [
    {
        "folder": "01_Nature_Macro",
        "slug": "makro",
        "title": "Макро",
        "place": "Природа",
        "description": "Цветы, мох, грибы и фактуры крупным планом — то, что обычно проходит незамеченным.",
    },
    {
        "folder": "02_Nature_Landscape",
        "slug": "pejzazh",
        "title": "Пейзаж",
        "place": "Алтай и лес",
        "description": "Горы, реки, долины и лес: Алтай, парки и тихие виды без суеты.",
    },
    {
        "folder": "03_City_Architecture",
        "slug": "gorod",
        "title": "Город и архитектура",
        "place": "Города",
        "description": "Фасады, парки, дворцы и улицы — Душанбе, Калининград, Пхукет и другие города.",
    },
    {
        "folder": "04_Travel_Coast_Sea",
        "slug": "more",
        "title": "Море и побережье",
        "place": "Балтика и океан",
        "description": "Дюны, буны, променады и закаты — Балтика и морские берега.",
    },
    {
        "folder": "05_Animals",
        "slug": "zhivotnye",
        "title": "Животные",
        "place": "Живая природа",
        "description": "Портреты и сцены: от дворового кота до сов, бурундуков и аквариума.",
    },
    {
        "folder": "06_People_Editorial",
        "slug": "lyudi",
        "title": "Люди",
        "place": "Улица",
        "description": "Документальные кадры: рынки, парки, туристы и повседневная жизнь города.",
    },
    {
        "folder": "07_Culture_Religion",
        "slug": "kultura",
        "title": "Культура и храмы",
        "place": "Храмы и памятники",
        "description": "Храмы, соборы, святилища и историческая архитектура в поездках.",
    },
    {
        "folder": "08_Transport_Streets",
        "slug": "ulicy",
        "title": "Улицы и транспорт",
        "place": "Городское движение",
        "description": "Перекрёстки, скутеры, мосты и ритм улицы — от Пхукета до Белграда.",
    },
    {
        "folder": "09_Holiday_Backgrounds",
        "slug": "prazdnik",
        "title": "Праздник",
        "place": "Новый год",
        "description": "Ёлочные шары, гирлянды и тёплый боке — праздничные фактуры крупным планом.",
    },
]


def log(msg: str) -> None:
    print(msg, flush=True)


def yaml_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fingerprint(path: Path) -> str:
    size = path.stat().st_size
    h = hashlib.md5()
    h.update(str(size).encode())
    with path.open("rb") as f:
        h.update(f.read(65536))
        if size > 131072:
            f.seek(-65536, os.SEEK_END)
            h.update(f.read(65536))
    return h.hexdigest()


def load_meta() -> dict[str, dict]:
    meta: dict[str, dict] = {}
    ru = SRC / "shutterstock_metadata_ru.csv"
    with ru.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("Имя файла") or "").strip()
            if not name:
                continue
            meta[name] = {"desc": (row.get("Описание") or "").strip()}
    dates = SRC / "editorial_list.csv"
    if dates.exists():
        with dates.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                name = (row.get("Имя файла") or "").strip()
                raw = (row.get("Дата съёмки") or "").strip()
                if name and raw and name in meta:
                    try:
                        meta[name]["date"] = datetime.strptime(raw, "%d.%m.%Y")
                    except ValueError:
                        pass
    return meta


def list_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in EXTS
    )


def resize_copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp.jpg")
    subprocess.run(
        [
            "sips",
            "-Z",
            str(MAX_EDGE),
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            str(JPEG_Q),
            str(src),
            "--out",
            str(tmp),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    tmp.replace(dest)


RU_MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня",
             "июля", "августа", "сентября", "октября", "ноября", "декабря"]

PLACES = [
    ("kaliningrad", "Калининград"), ("zelenogradsk", "Зеленоградск"),
    ("svetlogorsk", "Светлогорск"), ("baltic", "Балтика"),
    ("dushanbe", "Душанбе"), ("belgrade", "Белград"), ("phuket", "Пхукет"),
    ("altai", "Алтай"), ("altay", "Алтай"), ("moscow", "Москва"),
    ("tambov", "Тамбов"), ("yekaterinburg", "Екатеринбург"),
]

def detect_place(name: str, desc: str, default: str) -> str:
    hay = name.lower() + " " + desc.lower()
    for key, place in PLACES:
        if key in hay:
            return place
    for place in ("Калининград", "Зеленоградск", "Светлогорск", "Душанбе",
                  "Белград", "Пхукет", "Алтай", "Москва", "Тамбов"):
        if place.lower() in hay:
            return place
    return default


def exif_info(path: Path) -> dict:
    try:
        from PIL import Image, ExifTags
        ex = Image.open(path)._getexif() or {}
        tags = {ExifTags.TAGS.get(k, k): v for k, v in ex.items()}
    except Exception:
        return {}
    out: dict = {}
    raw = tags.get("DateTimeOriginal") or tags.get("DateTime")
    if raw:
        try:
            out["date"] = datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S")
        except ValueError:
            pass
    model = str(tags.get("Model") or "").strip()
    lens = str(tags.get("LensModel") or "").strip()
    for junk in ("Canon ",):
        model = model.replace(junk, "")
        lens = lens.replace(junk, "")
    gear = " · ".join(x for x in (("Canon " + model) if model else "", lens) if x)
    if gear:
        out["gear"] = gear
    return out


def caption_from_name(name: str) -> str:
    stem = Path(name).stem.replace("_", "-")
    words = [w for w in stem.split("-") if w and not w.isdigit()]
    return " ".join(words).capitalize() if words else stem


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"names": [], "fps": [], "photos": {}}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def write_album(album: dict, photos: list[dict]) -> None:
    if not photos:
        return
    dates = [p["date"] for p in photos if p.get("date")]
    album_date = max(dates) if dates else datetime(2026, 8, 29)
    cover = photos[0]
    lines = [
        "---",
        f"title: {yaml_quote(album['title'])}",
        f"description: {yaml_quote(album['description'])}",
        f"date: {album_date.strftime('%Y-%m-%d')}T12:00:00+03:00",
        "draft: false",
        f"place: {yaml_quote(album['place'])}",
        "gear: \"Canon EOS R8\"",
        f"cover: {yaml_quote(cover['src'])}",
        "photos:",
    ]
    for p in photos:
        lines.append(f"  - src: {yaml_quote(p['src'])}")
        lines.append(f"    alt: {yaml_quote(p['alt'])}")
        lines.append(f"    caption: {yaml_quote(p['caption'])}")
        if p.get("meta"):
            lines.append(f"    meta: {yaml_quote(p['meta'])}")
    lines += ["---", "", album["description"], ""]
    path = CONTENT / f"{album['slug']}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    log(f"альбом {path.name}: {len(photos)} кадров")


def process_album(album: dict, meta: dict, state: dict) -> None:
    folder = SRC / album["folder"]
    log(f"=== {album['folder']} ===")
    files = list_images(folder)
    log(f"файлов в папке: {len(files)}")
    dest_dir = DEST / album["slug"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    photos = list(state["photos"].get(album["slug"], []))
    already = {Path(p["src"]).name for p in photos}

    for i, src in enumerate(files, 1):
        dest_name = src.stem + ".jpg"
        key = src.name.lower()
        if key in state["names"] and dest_name not in already:
            log(f"  skip name  {src.name}")
            continue
        if dest_name in already:
            log(f"  already    {src.name}")
            state["names"] = list(set(state["names"]) | {key})
            continue

        fp = fingerprint(src)
        if fp in state["fps"]:
            log(f"  skip hash  {src.name}")
            continue

        dest = dest_dir / dest_name
        log(f"  [{i}/{len(files)}] {src.name}")
        try:
            resize_copy(src, dest)
        except subprocess.CalledProcessError as e:
            log(f"  ERROR sips: {e.stderr.decode(errors='replace')[:200]}")
            continue

        info = meta.get(src.name, {})
        desc = info.get("desc") or caption_from_name(src.name)
        ex = exif_info(src)
        shot = ex.get("date") or info.get("date")
        place = detect_place(src.name, desc, album["place"])
        bits = [place]
        if shot:
            bits.append(f"{shot.day} {RU_MONTHS[shot.month - 1]} {shot.year}")
        if ex.get("gear"):
            bits.append(ex["gear"])
        rec = {
            "src": f"/images/gallery/{album['slug']}/{dest.name}",
            "alt": desc,
            "caption": desc,
            "meta": " · ".join(bits),
            "date": shot.isoformat() if shot else None,
        }
        photos.append(rec)
        state["names"].append(key)
        state["fps"].append(fp)
        state["photos"][album["slug"]] = photos
        save_state(state)

    # restore datetime objects for album date
    for p in photos:
        if isinstance(p.get("date"), str):
            try:
                p["date"] = datetime.fromisoformat(p["date"])
            except ValueError:
                p["date"] = None
    write_album(album, photos)
    state["photos"][album["slug"]] = [
        {**p, "date": p["date"].isoformat() if isinstance(p.get("date"), datetime) else p.get("date")}
        for p in photos
    ]
    save_state(state)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="folder prefix, e.g. 01 or 01_Nature_Macro")
    args = parser.parse_args()

    if not SRC.is_dir():
        log(f"Нет папки: {SRC}")
        return 1

    albums = ALBUMS
    if args.only:
        albums = [a for a in ALBUMS if a["folder"].startswith(args.only)]
        if not albums:
            log(f"нет альбома: {args.only}")
            return 1

    log("Читаю метаданные…")
    meta = load_meta()
    log(f"В CSV описаний: {len(meta)}")
    state = load_state()

    for album in albums:
        process_album(album, meta, state)

    total = sum(len(v) for v in state["photos"].values())
    log(f"\nИтого уникальных в состоянии: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
