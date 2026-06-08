#!/usr/bin/env python3
"""
Зеркалирование контента сайта в Obsidian-vault.

Что синхронизируется:
  - content/_index.md       → <vault>/Starodubov.pro/index.md
  - content/now/_index.md   → <vault>/Starodubov.pro/now.md
  - content/posts/*.md      → <vault>/Starodubov.pro/posts/   (только RU)
  - картинки из static/images/, на которые ссылаются файлы выше
                            → <vault>/Starodubov.pro/attachments/

Пути картинок в Markdown переписываются на относительные, чтобы
работало в любом vault'е без настройки attachment folder:
  - из posts/*.md → ../attachments/...
  - из корня     → attachments/...

Использование:
    python3 scripts/sync_to_obsidian.py
    python3 scripts/sync_to_obsidian.py --vault /custom/path
    python3 scripts/sync_to_obsidian.py --include-en        # ещё и EN
    python3 scripts/sync_to_obsidian.py --dry-run

По умолчанию ищет vault по адресу:
    ~/Library/Mobile Documents/iCloud~md~obsidian/Documents
"""

from __future__ import annotations

import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path

DEFAULT_VAULT = Path.home() / 'Library/Mobile Documents/iCloud~md~obsidian/Documents'
DEST_NAME = 'Starodubov.pro'

IMG_INLINE_RE = re.compile(r'!\[[^\]]*\]\((/images/[^) ]+)')
IMG_COVER_RE = re.compile(r'^(\s*image:\s*")(/images/[^"]+)', re.M)


def find_project_root(start: Path) -> Path:
    """Up from script path, find first dir containing config/_default/hugo.yaml."""
    for d in (start, *start.parents):
        if (d / 'config' / '_default' / 'hugo.yaml').exists():
            return d
    raise SystemExit(f"Не нашёл корень Hugo-проекта от {start}")


def collect_md(root: Path, include_en: bool) -> tuple[list[Path], dict[str, Path]]:
    """Returns (posts, special) where special = {'index': home, 'now': now}."""
    if include_en:
        posts = sorted((root / 'content/posts').glob('*.md'))
    else:
        posts = sorted(
            p for p in (root / 'content/posts').glob('*.md')
            if not p.name.endswith('.en.md')
        )
    special: dict[str, Path] = {}
    home = root / 'content/_index.md'
    now = root / 'content/now/_index.md'
    if home.exists():
        special['index'] = home
    if now.exists():
        special['now'] = now
    return posts, special


def referenced_images(md_files: list[Path]) -> set[str]:
    """All distinct /images/... paths referenced in markdown or YAML cover."""
    paths: set[str] = set()
    for p in md_files:
        text = p.read_text(encoding='utf-8')
        paths.update(m.group(1) for m in IMG_INLINE_RE.finditer(text))
        paths.update(m.group(2) for m in IMG_COVER_RE.finditer(text))
    return paths


def rewrite(text: str, prefix: str) -> str:
    """Rewrite /images/... to <prefix>... in both inline markdown and YAML."""
    text = re.sub(r'(\]\()/images/', r'\1' + prefix, text)
    text = re.sub(
        r'^(\s*image:\s*")/images/',
        r'\1' + prefix,
        text,
        flags=re.M,
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--vault', type=Path, default=DEFAULT_VAULT,
                        help='путь к корню Obsidian vault (по умолчанию iCloud)')
    parser.add_argument('--include-en', action='store_true',
                        help='скопировать ещё и EN-версии постов в posts/en/')
    parser.add_argument('--dry-run', action='store_true',
                        help='показать план без фактического копирования')
    args = parser.parse_args()

    root = find_project_root(Path(__file__).resolve().parent)
    if not args.vault.exists():
        print(f"❌ Vault не найден: {args.vault}", file=sys.stderr)
        return 1

    dest = args.vault / DEST_NAME
    posts_dir = dest / 'posts'
    en_dir = posts_dir / 'en'
    att_dir = dest / 'attachments'

    posts, special = collect_md(root, include_en=args.include_en)
    ru_posts = [p for p in posts if not p.name.endswith('.en.md')]
    en_posts = [p for p in posts if p.name.endswith('.en.md')]
    all_md = list(posts) + list(special.values())
    images = referenced_images(all_md)

    print(f"Project root: {root}")
    print(f"Destination : {dest}")
    print(f"RU posts    : {len(ru_posts)}")
    if args.include_en:
        print(f"EN posts    : {len(en_posts)}")
    print(f"Special     : {sorted(special)}")
    print(f"Images      : {len(images)} referenced")

    if args.dry_run:
        print("\n[dry-run] — ничего не пишу")
        return 0

    posts_dir.mkdir(parents=True, exist_ok=True)
    att_dir.mkdir(parents=True, exist_ok=True)
    if args.include_en:
        en_dir.mkdir(parents=True, exist_ok=True)

    # === images
    copied, missing = 0, []
    for p in images:
        src = root / ('static' + p)  # /images/x.jpg → static/images/x.jpg
        if not src.exists():
            missing.append(p)
            continue
        rel = p.lstrip('/').removeprefix('images/')
        dst = att_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
            copied += 1
    print(f"\nImages: {copied} copied / {len(missing)} missing")
    for m in missing:
        print(f"  ⚠️  missing source: {m}")

    # === RU posts → posts/   (prefix ../attachments/)
    for p in ru_posts:
        out = posts_dir / p.name
        out.write_text(rewrite(p.read_text(encoding='utf-8'), '../attachments/'), encoding='utf-8')

    # === EN posts → posts/en/   (prefix ../../attachments/)
    if args.include_en:
        for p in en_posts:
            out = en_dir / p.name.replace('.en.md', '.md')
            out.write_text(rewrite(p.read_text(encoding='utf-8'), '../../attachments/'), encoding='utf-8')

    # === special: index.md, now.md   (prefix attachments/)
    name_map = {'index': 'index.md', 'now': 'now.md'}
    for key, src in special.items():
        out = dest / name_map[key]
        out.write_text(rewrite(src.read_text(encoding='utf-8'), 'attachments/'), encoding='utf-8')

    # === README
    readme = dedent_readme(datetime.date.today().isoformat(), include_en=args.include_en)
    (dest / 'README.md').write_text(readme, encoding='utf-8')

    print(f"\n✅ Готово: {dest}")
    total_md = sum(1 for _ in dest.rglob('*.md'))
    total_att = sum(1 for _ in att_dir.rglob('*') if _.is_file())
    print(f"   {total_md} md / {total_att} attachments")
    return 0


def dedent_readme(date: str, include_en: bool) -> str:
    en_block = '- `posts/en/` — EN-переводы\n' if include_en else ''
    return (
        f"# Starodubov.pro — зеркало сайта в базе знаний\n\n"
        f"Папка зеркалит [starodubov.pro](https://starodubov.pro/).\n\n"
        f"## Структура\n\n"
        f"- `index.md` — главная (bio)\n"
        f"- `now.md` — текущая страница /now/\n"
        f"- `posts/` — статьи блога (RU)\n"
        f"{en_block}"
        f"- `attachments/` — изображения\n\n"
        f"Пути к картинкам относительные, работает без настройки vault'а.\n\n"
        f"## Синхронизация\n\n"
        f"```bash\n"
        f"python3 scripts/sync_to_obsidian.py\n"
        f"python3 scripts/sync_to_obsidian.py --include-en  # +EN\n"
        f"```\n\n"
        f"Последняя синхронизация: {date}\n"
    )


if __name__ == '__main__':
    sys.exit(main())
