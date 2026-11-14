"""Build the three SVG illustrations for the October 2026 incident articles."""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static/images/october-2026"
OUT.mkdir(parents=True, exist_ok=True)

BG = "#101513"
PANEL = "#18211c"
LINE = "#34483b"
INK = "#f1f5ef"
MUTED = "#b1bdb3"
GREEN = "#7de4a0"
AMBER = "#f1cc7e"
RED = "#ff9b90"


def text(x, y, value, size=26, color=INK, weight=400, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def rect(x, y, w, h, stroke=LINE, fill=PANEL, radius=18):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )


def path(d, color=GREEN, arrow=True, dashed=False):
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3" '
        f'stroke-linecap="round" stroke-linejoin="round"'
        + (' marker-end="url(#arrow)"' if arrow else "")
        + (' stroke-dasharray="7 7"' if dashed else "")
        + "/>"
    )


def node(x, y, w, title, sub, color=LINE):
    return "".join([
        rect(x, y, w, 100, color),
        text(x + 24, y + 42, title, 27, INK, 600),
        text(x + 24, y + 77, sub, 22, MUTED),
    ])


def save(name, height, title, desc, elements):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}" role="img" aria-labelledby="title desc" lang="ru">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(desc)}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="context-stroke"/></marker></defs>
<rect width="800" height="{height}" rx="24" fill="{BG}"/>
<g font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif">
{''.join(elements)}
</g></svg>'''
    (OUT / name).write_text(svg, encoding="utf-8")


save(
    "openclaw-architecture.svg", 1020,
    "Доступ к OpenClaw и пять специалистов",
    "Браузер подключается через центральный Nginx и Nginx в Debian VM к Gateway. "
    "Telegram подключён к тому же Gateway. Gateway обращается к Luna и Sol и "
    "передаёт задания пяти специалистам по очереди. Профили используют общий Gateway.",
    [
        text(40, 60, "Как устроен мой OpenClaw", 36, INK, 650),
        text(40, 98, "Доступ и роли · 31 октября 2026", 23, MUTED),
        node(40, 140, 340, "Браузер", "Домашняя сеть"),
        node(420, 140, 340, "Telegram", "Обычный бот"),
        path("M210 240 V285"),
        node(40, 285, 340, "Центральный Nginx", "HTTPS · openclaw.home"),
        path("M210 385 V430"),
        node(40, 430, 340, "Nginx в Debian VM", "HTTPS · порт 18789"),
        node(420, 430, 340, "Модели Luna / Sol", "Общий аккаунт OpenAI"),
        path("M210 530 V590"),
        path("M760 190 H780 V640 H760"),
        rect(40, 590, 720, 130, GREEN),
        text(68, 635, "Gateway · main", 32, GREEN, 650),
        text(68, 675, "В Debian VM · 127.0.0.1:18790", 25, MUTED),
        path("M590 590 V530"),
        path("M400 720 V780"),
        rect(40, 780, 720, 140),
        text(68, 825, "Пять специалистов", 30, INK, 600),
        text(68, 863, "admin · researcher · developer", 26, GREEN),
        text(68, 898, "editor · planner", 26, GREEN),
        text(40, 965, "По очереди, без вложенного делегирования.", 25, MUTED),
        text(40, 1000, "Общий Gateway; профили не изолированы отдельными VM.", 23, MUTED),
    ],
)


save(
    "wd60efrx-timeline.svg", 1070,
    "Рост SMART 5 и хронология отказа WD60EFRX",
    "SMART 5: 243 на 24 октября, 296 на 25 и 26 октября. На 26 октября SMART "
    "ещё показывал PASSED, ZFS ONLINE. 29 октября в 20:42 возникли ошибки "
    "идентификации и UAS. 30 октября в 01:30 невосстановимые ошибки чтения "
    "перевели пул в SUSPENDED. 31 октября завершено отсоединение пула. "
    "296 не является универсальным порогом отказа.",
    [
        text(40, 60, "SMART: статус и динамика", 36, INK, 650),
        text(40, 98, "WD60EFRX · октябрь 2026", 23, MUTED),
        text(40, 132, "Переназначенные сектора · SMART 5", 25, MUTED),
        path("M100 310 H700", LINE, arrow=False),
        path("M130 285 L400 195 H670", AMBER, arrow=False),
        '<g fill="#f1cc7e"><circle cx="130" cy="285" r="7"/><circle cx="400" cy="195" r="7"/><circle cx="670" cy="195" r="7"/></g>',
        text(130, 258, "243", 36, INK, 650, "middle"),
        text(400, 176, "296", 36, INK, 650, "middle"),
        text(670, 176, "296", 36, INK, 650, "middle"),
        text(130, 349, "24 октября", 24, MUTED, anchor="middle"),
        text(400, 349, "25 октября", 24, MUTED, anchor="middle"),
        text(670, 349, "26 октября", 24, MUTED, anchor="middle"),
        text(530, 273, "+53 за интервал", 26, AMBER, 600, "middle"),
        rect(40, 390, 720, 80, GREEN),
        text(400, 440, "26 октября: SMART PASSED · ZFS ONLINE", 27, GREEN, 600, "middle"),
        path("M68 530 V925", LINE, arrow=False),
        '<circle cx="68" cy="550" r="9" fill="#f1cc7e"/>',
        text(100, 551, "29 октября · 20:42", 28, AMBER, 600),
        text(100, 589, "Зависла ATA-идентификация.", 25),
        text(100, 624, "UAS-ошибки, сброс USB-подключения.", 25, MUTED),
        '<circle cx="68" cy="700" r="9" fill="#ff9b90"/>',
        text(100, 701, "30 октября · 01:30", 28, RED, 600),
        text(100, 739, "Невосстановимые ошибки чтения.", 25),
        text(100, 774, "BackUP переходит в SUSPENDED.", 25, RED),
        '<circle cx="68" cy="850" r="9" fill="#b1bdb3"/>',
        text(100, 851, "31 октября", 28, INK, 600),
        text(100, 889, "Пул отсоединён от TrueNAS.", 25),
        text(100, 924, "Рабочие пулы снова проверены.", 25, MUTED),
        rect(40, 970, 720, 70, LINE, BG),
        text(400, 1014, "296 не является универсальным порогом отказа.", 25, MUTED, anchor="middle"),
    ],
)


save(
    "vaultwarden-backup-failure.svg", 1030,
    "Почему отказ резервного диска оставил Vaultwarden выключенным",
    "В 02:45 скрипт остановил Vaultwarden. В finally удаление частичного "
    "архива на недоступном BackUP завершилось ошибкой, поэтому последующий "
    "запуск контейнера не выполнился. Панель возвращала HTTP 502, хотя app.query "
    "показывал RUNNING. После исправления место назначения проверяется до "
    "остановки, а запуск выполняется во вложенном finally.",
    [
        text(40, 60, "Как бэкап остановил Vaultwarden", 35, INK, 650),
        text(40, 98, "Цепочка ошибки · 30 октября 2026", 23, MUTED),
        node(40, 140, 720, "02:45 · скрипт останавливает контейнер", "Начинается согласованное резервирование"),
        path("M400 240 V285", AMBER),
        node(40, 285, 720, "Очистка частичного архива в finally", "Файл находится на недоступном BackUP", AMBER),
        path("M400 385 V430", RED),
        node(40, 430, 720, "Удаление файла завершается ошибкой", "Выполнение не доходит до команды запуска", RED),
        path("M400 530 V575", RED),
        node(40, 575, 720, "Vaultwarden остаётся выключенным", "Панель: HTTP 502 · app.query: RUNNING", RED),
        rect(40, 730, 720, 250, GREEN),
        text(68, 777, "После исправления", 32, GREEN, 650),
        text(68, 824, "До остановки: проверить пул", 27),
        text(68, 860, "и пробную запись с fsync.", 27),
        text(68, 913, "Запуск контейнера: во вложенном finally,", 27),
        text(68, 949, "даже если очистка завершилась ошибкой.", 27),
    ],
)

print(f"Created 3 SVG illustrations in {OUT}")
