#!/usr/bin/env python3
"""Обложки с рисованными от руки сценками и людьми. Рендер в 2x с даунскейлом."""
import os, re, math, random, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images")
SC = os.path.join(tempfile.gettempdir(), "starodubov-cover-fonts")   # кэш TTF
S = 2                                   # суперсэмплинг

def prepare_fonts():
    """Шрифты сайта лежат в woff2; Pillow нужен TTF — конвертируем один раз (pip: fonttools brotli)."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    os.makedirs(SC, exist_ok=True)
    src = os.path.join(ROOT, "static", "fonts")
    for name, (f, w) in {
        "manrope700cyr": ("manrope-cyrillic-wght-normal.woff2", 700),
        "manrope700lat": ("manrope-latin-wght-normal.woff2", 700),
        "manrope500cyr": ("manrope-cyrillic-wght-normal.woff2", 500),
        "manrope500lat": ("manrope-latin-wght-normal.woff2", 500),
        "mono600cyr": ("jetbrains-mono-cyrillic-wght-normal.woff2", 600),
        "mono600lat": ("jetbrains-mono-latin-wght-normal.woff2", 600),
    }.items():
        dst = os.path.join(SC, name + ".ttf")
        if os.path.exists(dst):
            continue
        font = TTFont(os.path.join(src, f)); font.flavor = None
        if "fvar" in font:
            instantiateVariableFont(font, {"wght": w}, inplace=True)
        font.save(dst)
W, H = 1600, 900
ACC = (110, 231, 150); BLUE = (126, 178, 235); INK = (244, 244, 242)
MUT = (196, 196, 194); DIM = (150, 150, 148); BG = (10, 10, 11); CARD = (18, 18, 21)
AMB = (240, 196, 96); CORAL = (236, 130, 110); SKIN = (238, 196, 160); SKIN2 = (196, 140, 104)
LILAC = (176, 150, 230); PAPER = (236, 232, 222); LINE = (44, 44, 50)
CYR = re.compile(r'[А-Яа-яЁё]')
rnd = random.Random(7)

def F(name, size):
    return ImageFont.truetype(os.path.join(SC, name + ".ttf"), size * S)

class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W * S, H * S), BG)
        self.d = ImageDraw.Draw(self.img)
        for gx in range(0, W, 100):
            self.d.line([gx * S, 0, gx * S, H * S], fill=(17, 17, 19), width=S)
        for gy in range(0, H, 100):
            self.d.line([0, gy * S, W * S, gy * S], fill=(17, 17, 19), width=S)
        self.d.rectangle([0, 0, 10 * S, H * S], fill=ACC)

    # ---------- текст ----------
    def text(self, x, y, s, cyr, lat, fill, tracking=0):
        x *= S; y *= S
        for ch in s:
            f = cyr if CYR.match(ch) else lat
            self.d.text((x, y), ch, font=f, fill=fill)
            x += self.d.textlength(ch, font=f) + tracking * S
        return x / S

    def layout(self, badge, t1, t2, s1, s2, head=92):
        hc, hl = F("manrope700cyr", head), F("manrope700lat", head)
        sc, sl = F("manrope500cyr", 33), F("manrope500lat", 33)
        mc, ml = F("mono600cyr", 26), F("mono600lat", 26)
        X = 84
        sub2 = H - 76 - 42; sub1 = sub2 - 46
        ty2 = sub1 - 36 - (head + 20); ty1 = ty2 - (head + 12); by = ty1 - 64
        self.d.ellipse([X * S, (by + 9) * S, (X + 13) * S, (by + 22) * S], fill=ACC)
        bx = X + 33
        for i, part in enumerate(badge):
            if i:
                bx += 22
                self.d.ellipse([bx * S, (by + 12) * S, (bx + 6) * S, (by + 18) * S], fill=ACC)
                bx += 28
            bx = self.text(bx, by, part, mc, ml, ACC, tracking=4)
        self.text(X - 4, ty1, t1, hc, hl, INK)
        self.text(X - 4, ty2, t2, hc, hl, ACC)
        self.text(X, sub1, s1, sc, sl, MUT)
        self.text(X, sub2, s2, sc, sl, MUT)

    # ---------- «карандаш» ----------
    def _wob(self, pts, amp=1.6, step=14):
        out = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(int(math.hypot(x1 - x0, y1 - y0) // step), 1)
            for i in range(n):
                t = i / n
                out.append(((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp)) * S,
                            (y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)) * S))
        out.append((pts[-1][0] * S, pts[-1][1] * S))
        return out

    def line(self, pts, fill=INK, width=4, amp=1.6):
        self.d.line(self._wob(pts, amp), fill=fill, width=width * S, joint="curve")

    def poly(self, pts, fill, outline=None, width=4, amp=1.8):
        p = self._wob(pts + [pts[0]], amp)
        self.d.polygon(p, fill=fill)
        if outline:
            self.d.line(p, fill=outline, width=width * S, joint="curve")

    def blob(self, cx, cy, rx, ry, fill, outline=None, width=4, amp=1.5, n=28, a0=0, a1=360):
        pts = []
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + rx * math.cos(a) + rnd.uniform(-amp, amp),
                        cy + ry * math.sin(a) + rnd.uniform(-amp, amp)))
        p = [(x * S, y * S) for x, y in pts]
        if fill:
            self.d.polygon(p, fill=fill)
        if outline:
            self.d.line(p, fill=outline, width=width * S, joint="curve")

    def arc(self, cx, cy, rx, ry, a0, a1, fill=INK, width=4, n=16):
        pts = [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        self.line(pts, fill, width, amp=0.8)

    def rrect(self, x0, y0, x1, y1, fill, outline=None, width=4, r=14):
        pts = [(x0 + r, y0), (x1 - r, y0), (x1, y0 + r), (x1, y1 - r),
               (x1 - r, y1), (x0 + r, y1), (x0, y1 - r), (x0, y0 + r)]
        self.poly(pts, fill, outline, width)

    def arrow(self, x0, y0, x1, y1, fill=ACC, width=5, dashed=False):
        if dashed:
            L = math.hypot(x1 - x0, y1 - y0); n = max(int(L // 30), 1)
            for i in range(n):
                t0, t1 = i / n, (i + 0.55) / n
                self.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                           (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill, width)
        else:
            self.line([(x0, y0), (x1, y1)], fill, width)
        a = math.atan2(y1 - y0, x1 - x0)
        for s in (0.5, -0.5):
            self.line([(x1, y1), (x1 - 22 * math.cos(a - s), y1 - 22 * math.sin(a - s))], fill, width)

    def label(self, x, y, s, fill=DIM, size=22):
        self.text(x, y, s, F("mono600cyr", size), F("mono600lat", size), fill, tracking=2)

    # ---------- человек ----------
    def person(self, x, y, shirt=AMB, skin=SKIN, hair=(60, 44, 36), lhand=None, rhand=None,
               sit=False, look=0, hairstyle="short", k=1.0, smile=True):
        """x, y — точка под ногами (или под сиденьем при sit). Возвращает координаты головы."""
        hip_y = y - 118 * k
        sh_y = hip_y - 104 * k
        head_y = sh_y - 46 * k
        pants = (58, 70, 96)
        # ноги
        if sit:
            for sx in (-16, 16):
                self.line([(x + sx * k, hip_y), (x + (sx + 62) * k, hip_y + 6 * k),
                           (x + (sx + 66) * k, y)], pants, int(20 * k), amp=1.0)
                self.blob(x + (sx + 78) * k, y, 20 * k, 9 * k, (30, 30, 34))
        else:
            for sx in (-17, 17):
                self.line([(x + sx * k, hip_y - 4 * k), (x + sx * 1.15 * k, y - 6 * k)], pants, int(22 * k), amp=1.0)
                self.blob(x + (sx * 1.15 + 8) * k, y, 21 * k, 9 * k, (30, 30, 34))
        # туловище (свитер)
        self.poly([(x - 40 * k, sh_y + 8 * k), (x - 24 * k, sh_y - 8 * k), (x + 24 * k, sh_y - 8 * k),
                   (x + 40 * k, sh_y + 8 * k), (x + 34 * k, hip_y + 6 * k), (x - 34 * k, hip_y + 6 * k)],
                  shirt, amp=1.4)
        # руки
        lh = lhand or (x - 58 * k, hip_y - 6 * k)
        rh = rhand or (x + 58 * k, hip_y - 6 * k)
        for (sx, hand) in ((-36, lh), (36, rh)):
            ex = (x + sx * k + hand[0]) / 2 + (sx / 36) * 10 * k
            ey = (sh_y + hand[1]) / 2 + 16 * k
            self.line([(x + sx * k, sh_y + 8 * k), (ex, ey), hand], shirt, int(18 * k), amp=1.0)
            self.blob(hand[0], hand[1], 11 * k, 11 * k, skin)
        # шея и голова
        self.line([(x, sh_y - 6 * k), (x, head_y + 26 * k)], skin, int(16 * k), amp=0.5)
        self.blob(x, head_y, 34 * k, 37 * k, skin, amp=1.2)
        # волосы
        if hairstyle == "short":
            self.blob(x, head_y - 12 * k, 36 * k, 28 * k, hair, a0=180, a1=360, amp=2.0)
            self.blob(x - 4 * k, head_y - 30 * k, 26 * k, 12 * k, hair, amp=2.0)
        elif hairstyle == "long":
            self.blob(x, head_y - 10 * k, 38 * k, 30 * k, hair, a0=170, a1=370, amp=2.0)
            self.poly([(x - 38 * k, head_y - 8 * k), (x - 30 * k, head_y + 52 * k), (x - 18 * k, head_y + 30 * k),
                       (x - 22 * k, head_y - 6 * k)], hair)
            self.poly([(x + 38 * k, head_y - 8 * k), (x + 30 * k, head_y + 52 * k), (x + 18 * k, head_y + 30 * k),
                       (x + 22 * k, head_y - 6 * k)], hair)
        elif hairstyle == "bun":
            self.blob(x, head_y - 12 * k, 36 * k, 28 * k, hair, a0=180, a1=360, amp=2.0)
            self.blob(x + 6 * k, head_y - 46 * k, 15 * k, 14 * k, hair, amp=1.6)
        # лицо
        ex = look * 5 * k
        for sx in (-13, 13):
            self.blob(x + sx * k + ex, head_y + 2 * k, 3.6 * k, 4.2 * k, (40, 34, 32), amp=0.3, n=10)
        if smile:
            self.arc(x + ex, head_y + 12 * k, 11 * k, 8 * k, 20, 160, (120, 60, 50), max(int(3 * k), 2))
        else:
            self.line([(x - 8 * k + ex, head_y + 19 * k), (x + 8 * k + ex, head_y + 17 * k)], (120, 60, 50), max(int(3 * k), 2), amp=0.4)
        return x, head_y

    def bubble(self, x, y, w, h, text, tail=(0, 0), fill=PAPER, col=(30, 30, 34)):
        fc, fl = F("manrope700cyr", 24), F("manrope700lat", 24)
        tw = sum(self.d.textlength(ch, font=(fc if CYR.match(ch) else fl)) for ch in text) / S
        w = max(w, tw + 44)                      # облачко всегда шире текста
        if x + w > W - 24:
            x = W - 24 - w
        self.rrect(x, y, x + w, y + h, fill, r=18)
        self.poly([(x + 30, y + h - 4), (x + 60, y + h - 4), (x + 30 + tail[0], y + h + 26 + tail[1])], fill)
        self.text(x + 20, y + (h - 30) / 2, text, F("manrope700cyr", 24), F("manrope700lat", 24), col)

    def cat(self, x, y, col=PAPER, k=1.0):
        self.blob(x, y, 30 * k, 26 * k, col, amp=1.2)
        self.poly([(x - 26 * k, y - 14 * k), (x - 20 * k, y - 42 * k), (x - 6 * k, y - 22 * k)], col)
        self.poly([(x + 26 * k, y - 14 * k), (x + 20 * k, y - 42 * k), (x + 6 * k, y - 22 * k)], col)
        for sx in (-10, 10):
            self.arc(x + sx * k, y - 2 * k, 5 * k, 4 * k, 200, 340, (40, 34, 32), 3)
        self.arc(x, y + 8 * k, 6 * k, 4 * k, 20, 160, (40, 34, 32), 3)

    def save(self, name):
        out = self.img.resize((W, H), Image.LANCZOS)
        out.save(os.path.join(OUT, name), quality=90)
        print("saved", name)


# ================= СЦЕНЫ =================

def cover_mama():
    c = Canvas()
    c.layout(["КНИГА", "МАРИНА ПЕРЕСКОКОВА"], "Мама,", "я тимлид!",
             "Практические советы по руководству IT-командой",
             "и мой взгляд после госслужбы и Банка России")
    # пол
    c.line([(1040, 640), (1570, 640)], LINE, 3)
    # тимлид с чашкой машет команде
    c.person(1160, 640, shirt=AMB, hairstyle="bun", hair=(90, 52, 40), lhand=(1092, 470), rhand=(1222, 520), look=1)
    c.rrect(1210, 500, 1240, 534, PAPER, r=6)                     # чашка
    c.bubble(1010, 250, 250, 70, "Ну что, стендап?", tail=(70, 10))
    # команда котов за ноутбуками
    for i, (cx, col) in enumerate(((1330, PAPER), (1430, BLUE), (1522, PAPER))):
        c.cat(cx, 548 - (i % 2) * 14, col, k=0.95)
        c.rrect(cx - 40, 590, cx + 40, 640, (40, 52, 74), outline=(80, 100, 130), width=3, r=8)
        c.blob(cx, 615, 7, 7, ACC, amp=0.4, n=10)
    c.save("mama-ya-timlid-cover.jpg")


def cover_benzin():
    c = Canvas()
    c.layout(["АВТО", "ТОПЛИВО", "2026"], "Бензин Евро-3", "вернулся",
             "Что будет с нашими моторами", "и кому стоит напрячься уже сейчас")
    c.line([(1040, 650), (1570, 650)], LINE, 3)
    # колонка
    c.rrect(1360, 300, 1530, 650, (28, 34, 44), outline=BLUE, width=4, r=18)
    c.rrect(1384, 328, 1506, 410, (8, 16, 11), outline=(60, 70, 80), width=3, r=10)
    c.label(1398, 340, "АИ-95", ACC, 30)
    c.label(1398, 378, "К5? К3?", AMB, 20)
    for i in range(3):
        c.rrect(1384 + i * 44, 432, 1418 + i * 44, 466, (36, 40, 48), r=8)
    # шланг к руке человека
    c.line([(1360, 470), (1320, 500), (1300, 470)], (70, 80, 96), 7, amp=2.2)
    # человек с пистолетом, озадачен
    hx, hy = c.person(1200, 650, shirt=CORAL, hairstyle="short", lhand=(1140, 548), rhand=(1296, 466), look=1, smile=False)
    c.rrect(1288, 446, 1330, 470, (70, 80, 96), r=6)              # пистолет
    c.text(1236, hy - 118, "?", F("manrope700cyr", 64), F("manrope700lat", 64), AMB)
    c.text(1276, hy - 92, "?", F("manrope700cyr", 40), F("manrope700lat", 40), AMB)
    # капля с «S»
    c.blob(1108, 360, 26, 30, (70, 60, 30), outline=AMB, width=3)
    c.text(1098, 340, "S", F("manrope700cyr", 32), F("manrope700lat", 32), AMB)
    c.label(1064, 402, "сера ×15", AMB, 20)
    c.save("benzin-evro3-cover.jpg")


def cover_vpn():
    c = Canvas()
    c.layout(["ГАЙД", "СЕТЬ", "SELF-HOSTED"], "Свой VPN", "на AmneziaWG",
             "Сервер за пятнадцать минут без консоли",
             "и выборочная маршрутизация на Keenetic")
    c.line([(1040, 660), (1570, 660)], LINE, 3)
    # домик-контур
    c.line([(1050, 400), (1200, 270), (1350, 400)], (70, 80, 96), 5, amp=2.0)
    c.line([(1076, 388), (1076, 660)], (70, 80, 96), 5); c.line([(1324, 388), (1324, 660)], (70, 80, 96), 5)
    # диван и человек с ноутбуком
    c.rrect(1096, 540, 1300, 640, (52, 44, 70), r=26)
    c.rrect(1088, 500, 1130, 640, (62, 52, 84), r=18)
    c.person(1176, 650, shirt=ACC, hairstyle="long", hair=(70, 40, 30), sit=True,
             lhand=(1196, 520), rhand=(1250, 524), look=1)
    c.poly([(1196, 530), (1276, 530), (1268, 480), (1204, 480)], (40, 52, 74), outline=(90, 110, 140), width=3)
    # роутер на полке
    c.rrect(1226, 410, 1306, 440, (28, 34, 44), outline=BLUE, width=3, r=8)
    c.line([(1240, 410), (1236, 376)], BLUE, 3); c.line([(1292, 410), (1296, 376)], BLUE, 3)
    # туннель к серверу-облаку
    c.arrow(1330, 424, 1440, 330, ACC, 5)
    c.blob(1490, 290, 62, 40, (24, 40, 30), outline=ACC, width=4)
    c.label(1462, 278, "VPS", ACC, 24)
    c.rrect(1370, 360, 1398, 384, (20, 30, 24), outline=ACC, width=3, r=5)   # замочек
    c.arc(1384, 360, 9, 12, 180, 360, ACC, 3)
    c.save("vpn-awg-keenetic-cover.jpg")


def cover_split():
    c = Canvas()
    c.layout(["ГАЙД", "AMNEZIAVPN", "ЧАСТЬ 2"], "Раздельное", "туннелирование",
             "Список сайтов уходит в туннель, всё остальное",
             "идёт напрямую. Настройка в самом приложении")
    c.line([(1040, 650), (1570, 650)], LINE, 3)
    # человек на ходу с телефоном
    c.person(1150, 650, shirt=BLUE, hairstyle="short", hair=(40, 36, 40), lhand=(1092, 540), rhand=(1216, 470), look=1)
    c.rrect(1204, 420, 1240, 486, (28, 34, 44), outline=PAPER, width=3, r=8)
    # две дороги
    c.arrow(1256, 440, 1430, 330, ACC, 6)
    c.arrow(1256, 470, 1430, 560, BLUE, 6, dashed=True)
    c.blob(1490, 300, 66, 42, (24, 40, 30), outline=ACC, width=4)
    c.label(1456, 288, "VPN", ACC, 24)
    c.rrect(1322, 366, 1350, 390, (20, 30, 24), outline=ACC, width=3, r=5); c.arc(1336, 366, 9, 12, 180, 360, ACC, 3)
    c.rrect(1434, 530, 1560, 600, (24, 30, 40), outline=BLUE, width=4, r=16)
    c.label(1452, 552, "БАНК", BLUE, 24)
    c.label(1296, 296, "список", ACC, 20)
    c.label(1300, 560, "остальное", BLUE, 20)
    c.save("amnezia-split-cover.jpg")


def cover_openapi():
    c = Canvas()
    c.layout(["ИБ", "ФИНТЕХ", "СТАНДАРТЫ"], "Безопасность", "Open API",
             "Архитектура, токены и защита от атак:",
             "от Zero Trust и FAPI до ГОСТ и стандартов ЦБ")
    c.line([(1040, 650), (1570, 650)], LINE, 3)
    # банкир и финтех-разработчица обмениваются ключом через «шлюз»
    c.person(1120, 650, shirt=(70, 90, 140), hairstyle="short", hair=(50, 50, 56), rhand=(1216, 488), lhand=(1064, 540), look=1)
    c.person(1490, 650, shirt=CORAL, hairstyle="long", hair=(96, 56, 36), lhand=(1394, 488), rhand=(1546, 540), look=-1)
    # щит-шлюз между ними
    c.poly([(1250, 380), (1360, 380), (1360, 500), (1305, 570), (1250, 500)], (20, 34, 26), outline=ACC, width=5)
    c.line([(1280, 470), (1300, 496), (1336, 440)], ACC, 7, amp=1.0)
    # ключ-токен
    c.blob(1222, 470, 12, 12, None, outline=AMB, width=4); c.line([(1234, 470), (1262, 470)], AMB, 4)
    c.line([(1256, 470), (1256, 482)], AMB, 4)
    c.label(1256, 330, "{ API }", BLUE, 30)
    c.label(1090, 690, "БАНК", DIM, 20); c.label(1446, 690, "ФИНТЕХ", DIM, 20)
    c.save("open-api-cover.jpg")


def cover_agents():
    c = Canvas()
    c.layout(["ИБ", "ИИ-АГЕНТЫ", "АВТОМАТИЗАЦИЯ"], "Рутину — агенту,", "риски — под контроль",
             "Как автоматизировать работу с помощью ИИ",
             "и не открыть новую поверхность атаки", head=88)
    c.line([(1076, 650), (1570, 650)], LINE, 3)
    # стол
    c.rrect(1240, 520, 1560, 540, (70, 56, 44), r=6)
    c.line([(1262, 540), (1262, 650)], (70, 56, 44), 8); c.line([(1538, 540), (1538, 650)], (70, 56, 44), 8)
    # робот за ноутбуком
    c.rrect(1400, 380, 1500, 470, (28, 34, 44), outline=BLUE, width=4, r=18)
    c.line([(1450, 380), (1450, 350)], BLUE, 4); c.blob(1450, 344, 7, 7, ACC, amp=0.4, n=10)
    for sx in (-22, 22):
        c.blob(1450 + sx, 418, 9, 9, (8, 16, 11), outline=ACC, width=3)
    c.arc(1450, 440, 14, 8, 20, 160, ACC, 3)
    c.rrect(1416, 474, 1484, 520, (36, 44, 58), r=10)
    c.poly([(1300, 520), (1390, 520), (1380, 462), (1310, 462)], (40, 52, 74), outline=(90, 110, 140), width=3)
    # человек с чашкой, рука на кнопке
    c.person(1140, 650, shirt=AMB, hairstyle="short", hair=(60, 44, 36), lhand=(1080, 500), rhand=(1232, 500), look=1)
    c.rrect(1062, 462, 1094, 500, PAPER, r=6)
    c.arc(1078, 452, 8, 10, 200, 340, DIM, 3)
    c.blob(1248, 506, 20, 12, CORAL, outline=(140, 60, 50), width=3)
    c.label(1196, 552, "STOP", CORAL, 20)
    c.bubble(1330, 250, 210, 66, "Можно деплоить?", tail=(60, 8))
    c.save("ai-agents-cover.jpg")


def cover_risk():
    c = Canvas()
    c.layout(["ИИ", "РИСКИ", "РАЗБОР ОТЧЁТА"], "Отчёт о рисках", "Anthropic",
             "Как ИИ-лаборатория проверяет саму себя",
             "и чему у неё поучиться безопасникам", head=88)
    c.line([(1040, 650), (1570, 650)], LINE, 3)
    # большой лист отчёта
    c.poly([(1290, 250), (1540, 262), (1528, 610), (1278, 598)], PAPER, amp=1.2)
    c.text(1312, 282, "RISK REPORT", F("mono600cyr", 24), F("mono600lat", 24), (30, 30, 34), tracking=2)
    for i, wl in enumerate((190, 170, 196, 140, 182, 120)):
        c.line([(1312, 336 + i * 30), (1312 + wl, 338 + i * 30)], (150, 146, 136), 4, amp=0.8)
    # шкала риска на листе
    for i, col in enumerate(((190, 200, 190), (60, 170, 100), (200, 190, 170), (200, 180, 176))):
        c.rrect(1312 + i * 52, 534, 1356 + i * 52, 558, col, r=8)
    c.arrow(1330, 522, 1384, 522, (200, 120, 40), 4)
    # человек с лупой
    c.person(1140, 650, shirt=LILAC, hairstyle="short", hair=(70, 50, 40), lhand=(1078, 540), rhand=(1250, 430), look=1)
    c.blob(1290, 400, 38, 38, (210, 230, 240), outline=(60, 60, 66), width=6)
    c.line([(1262, 426), (1246, 442)], (60, 60, 66), 8)
    c.text(1268, 380, "!", F("manrope700cyr", 44), F("manrope700lat", 44), CORAL)
    c.save("anthropic-risk-report-cover.jpg")


def cover_openclaw():
    c = Canvas()
    c.layout(["SELF-HOSTED", "ИИ-АГЕНТ", "ТОКЕНЫ"], "Домашний агент", "и экономия токенов",
             "OpenClaw в отдельной виртуалке на NAS:",
             "изоляция, модели и куда уходит контекст", head=88)
    c.line([(1040, 650), (1570, 650)], LINE, 3)
    # мини-сервер, внутри — «комната» VM с агентом
    c.rrect(1320, 400, 1560, 650, (24, 28, 36), outline=BLUE, width=4, r=18)
    c.label(1340, 412, "NAS", BLUE, 20)
    c.rrect(1350, 450, 1530, 620, (14, 22, 17), outline=ACC, width=3, r=14)
    c.label(1366, 458, "VM", ACC, 20)
    RED = (214, 84, 72)
    c.blob(1440, 552, 44, 42, RED, amp=1.4)                        # агент-клешня
    for sx in (-1, 1):
        c.blob(1440 + sx * 52, 540, 15, 13, RED, amp=1.2)          # клешни
        c.line([(1440 + sx * 12, 512), (1440 + sx * 20, 494)], RED, 4)   # усики
        c.blob(1440 + sx * 14, 544, 8, 9, PAPER, amp=0.4, n=12)
        c.blob(1440 + sx * 14, 546, 4, 4.5, (30, 26, 26), amp=0.2, n=10)
    c.arc(1440, 566, 12, 7, 20, 160, (110, 36, 30), 3)
    for i in range(3):
        c.blob(1350 + i * 22, 636, 5, 5, ACC if i < 2 else (60, 66, 76), amp=0.3, n=10)
    # человек с телефоном получает сводку
    c.person(1150, 650, shirt=AMB, hairstyle="short", hair=(60, 44, 36),
             lhand=(1090, 540), rhand=(1222, 474), look=1)
    c.rrect(1208, 424, 1244, 490, (28, 34, 44), outline=PAPER, width=3, r=8)
    c.arrow(1346, 500, 1262, 462, ACC, 4, dashed=True)
    c.bubble(1060, 236, 200, 66, "Сводка готова!", tail=(110, 12))
    # счётчик контекста
    c.label(1330, 300, "КОНТЕКСТ · 42%", DIM, 20)
    c.rrect(1330, 334, 1560, 352, (34, 36, 42), r=8)
    c.rrect(1330, 334, 1427, 352, AMB, r=8)
    c.save("openclaw-cover.jpg")


if __name__ == "__main__":
    import sys
    prepare_fonts()
    scenes = (cover_mama, cover_benzin, cover_vpn, cover_split, cover_openapi, cover_agents,
              cover_risk, cover_openclaw)
    wanted = sys.argv[1:]                # напр.: make_covers.py openclaw
    for fn in scenes:
        if not wanted or any(w in fn.__name__ for w in wanted):
            fn()
