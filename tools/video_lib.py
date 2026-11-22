#!/usr/bin/env python3
"""Git Hunter: вертикальные видео 1080x1920 (Shorts / Reels / TikTok) для каждого проекта подборки.

Слайды рисует Pillow, анимацию (панорама Кена Бёрнса + переходы), субтитры и звук собирает ffmpeg.
Также готовит тексты постов для YouTube / Instagram / TikTok.

Переменные окружения:
  VIDEO_DATE=2026-11-22   какой день обрабатывать (по умолчанию последний)
  VIDEO_FORCE=1           пересобрать даже если видео уже есть
  VIDEO_LIMIT=2           обработать только N проектов (для тестов)
  NO_RELEASE=1            не загружать в GitHub Release
"""
import asyncio
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CFG = {"site_url": "https://avtomaster24bot-lab.github.io/git-hunter-studio/", "voice": "ru-RU-SvetlanaNeural"}
SITE = CFG["site_url"].rstrip("/") + "/"
SITE_SHORT = SITE.replace("https://", "").rstrip("/")
REPO = os.environ.get("GITHUB_REPOSITORY", "avtomaster24bot-lab/git-hunter")
FONTS = ROOT / "assets" / "fonts"
VOICE = CFG.get("voice", "ru-RU-SvetlanaNeural")
W, H = 1080, 1920            # итоговое видео
PAN_X, PAN_Y = 64, 114       # запас под панораму
CW, CH = W + PAN_X, H + PAN_Y  # размер слайда
FPS = 30
TRANS = 0.5
END_CARD = 3.0
LEAD = 0.3                   # пауза перед голосом
MAX_LEN = 58.5
SUB_Y = 1340                 # центр субтитров (выше подписи TikTok/Reels)

BG = (11, 15, 23)
ACC = (124, 92, 255)
ACC2 = (34, 211, 238)
TXT = (235, 240, 248)
MUT = (150, 162, 182)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f"Inter-{weight}.ttf"), size)


# ------------------------------------------------------------------ рисование
def background(seed=0):
    img = Image.new("RGB", (CW, CH), BG)
    glow = Image.new("RGB", (CW, CH), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    spots = [((0.15, 0.08), ACC, 520), ((0.95, 0.35), ACC2, 420), ((0.2, 0.9), (91, 140, 255), 480)]
    for i, ((fx, fy), col, r) in enumerate(spots):
        fx = (fx + 0.13 * seed * (1 if i % 2 else -1)) % 1.0
        x, y = int(fx * CW), int(fy * CH)
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(c * 0.55) for c in col))
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    return Image.blend(img, glow, 0.6).convert("RGBA")


def wrap(draw, text, fnt, width):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, weight, width, height, max_size, min_size=34, spacing=1.25):
    size = max_size
    while True:
        f = font(weight, size)
        lines = wrap(draw, text, f, width)
        h = len(lines) * size * spacing
        if h <= height or size <= min_size:
            if h > height:  # обрезаем с многоточием
                n = max(1, int(height // (size * spacing)))
                lines = lines[:n]
                lines[-1] = lines[-1].rstrip(" ,.;:") + "…"
            return f, lines, size
        size -= 2


def draw_lines(draw, lines, f, size, x, y, fill, spacing=1.25):
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += int(size * spacing)
    return y


def logo(size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = Image.new("RGBA", (size, size))
    gd = ImageDraw.Draw(grad)
    for i in range(size):
        t = i / size
        gd.line([(0, i), (size, i)], fill=tuple(int(ACC[k] * (1 - t) + ACC2[k] * t) for k in range(3)) + (255,))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 4, fill=255)
    im.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(im)
    s = size / 64
    d.ellipse([16 * s, 16 * s, 40 * s, 40 * s], outline="white", width=max(2, int(5 * s)))
    d.line([37 * s, 37 * s, 48 * s, 48 * s], fill="white", width=max(3, int(6 * s)))
    d.line([24 * s, 28 * s, 27 * s, 31 * s, 33 * s, 25 * s], fill="white", width=max(2, int(3.5 * s)), joint="curve")
    return im


# зона контента в координатах слайда (видна при любом положении панорамы)
X0 = PAN_X + 72
X1 = CW - PAN_X - 110
CWID = X1 - X0
Y0 = PAN_Y + 70
Y_CONTENT_END = 1200  # ниже — субтитры и безопасная зона интерфейса TikTok/Reels


def header(img, d, label=None):
    lg = logo(64)
    img.alpha_composite(lg, (X0, Y0))
    d.text((X0 + 84, Y0 + 8), "Git Hunter Studio", font=font("ExtraBold", 40), fill=TXT)
    if label:
        f = font("SemiBold", 30)
        tw = d.textlength(label, font=f)
        d.rounded_rectangle([X1 - tw - 44, Y0 + 6, X1, Y0 + 60], radius=28, fill=(30, 38, 56), outline=(60, 72, 100), width=2)
        d.text((X1 - tw - 22, Y0 + 15), label, font=f, fill=TXT)


def fmt_num(n):
    n = int(n or 0)
    if n >= 1000:
        return (f"{n / 1000:.1f}".rstrip("0").rstrip(".") if n < 10000 else str(round(n / 1000))) + "k"
    return str(n)


def plural(n, a, b, c):
    n = abs(int(n)) % 100
    m = n % 10
    return a if m == 1 and n != 11 else b if 2 <= m <= 4 and not 12 <= n <= 14 else c


def load_image(urls):
    for u in urls:
        if not u:
            continue
        try:
            r = requests.get(u, timeout=30, headers={"User-Agent": "git-hunter"})
            if r.ok and len(r.content) > 2000:
                im = Image.open(io.BytesIO(r.content)).convert("RGB")
                if im.width >= 300 and im.height >= 150:
                    return im
        except Exception as e:  # noqa
            log("img fail", u, e)
    return None


def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r + 1), int(im.height * r + 1)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def contain(im, w, h):
    """Картинка целиком (без обрезки) на размытом фоне из неё же."""
    bg = cover(im, w, h).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new("RGB", (w, h), (10, 12, 20)), 0.45)
    r = min(w / im.width, h / im.height)
    fg = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    bg.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2))
    return bg


def rounded(im, radius=28):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def slide_title(p, pic, seed):
    img = background(seed)
    d = ImageDraw.Draw(img)
    header(img, d, p.get("category_name"))
    y = Y0 + 120
    if pic is not None:
        ph = int(CWID * (pic.height / pic.width)) if pic.width / pic.height > 1.2 else int(CWID * 0.75)
        ph = max(380, min(ph, 620))
        im = rounded(contain(pic, CWID, ph))
        sh = Image.new("RGBA", (CWID + 60, ph + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([30, 40, CWID + 30, ph + 30], radius=30, fill=(0, 0, 0, 150))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (X0 - 30, y - 30))
        img.alpha_composite(im, (X0, y))
        y += ph + 50
    f, lines, size = fit(d, p["name"], "ExtraBold", CWID, 230, 104, 56, 1.1)
    y = draw_lines(d, lines, f, size, X0, y, TXT, 1.1) + 6
    d.text((X0, y), "от " + p.get("owner", ""), font=font("Regular", 34), fill=MUT)
    y += 66
    stats = [f"★ {fmt_num(p['stars'])} " + ("звёзд" if p["stars"] >= 1000 else plural(p['stars'], 'звезда', 'звезды', 'звёзд'))]
    if p.get("language"):
        stats.append(p["language"])
    if p.get("stars_per_day"):
        stats.append(f"+{fmt_num(p['stars_per_day'])} в день")
    x = X0
    sf = font("SemiBold", 34)
    for i, s in enumerate(stats):
        tw = d.textlength(s, font=sf)
        col = (52, 211, 153) if "в день" in s else (251, 191, 36) if i == 0 else TXT
        d.rounded_rectangle([x, y, x + tw + 40, y + 62], radius=31, fill=(24, 31, 46), outline=(55, 66, 92), width=2)
        d.text((x + 20, y + 10), s, font=sf, fill=col)
        x += tw + 56
    y += 96
    tag = p["summary"].get("tagline", "")
    if tag and y < Y_CONTENT_END - 80:
        f, lines, size = fit(d, tag, "SemiBold", CWID, Y_CONTENT_END - y, 54, 36, 1.25)
        draw_lines(d, lines, f, size, X0, y, (196, 181, 253), 1.25)
    return img


def slide_text(label, text, seed, extra=None, accent=ACC2):
    img = background(seed)
    d = ImageDraw.Draw(img)
    header(img, d)
    y = Y0 + 170
    d.rounded_rectangle([X0, y + 8, X0 + 12, y + 92], radius=6, fill=accent)
    d.text((X0 + 36, y), label, font=font("ExtraBold", 84), fill=accent)
    y += 150
    avail = Y_CONTENT_END - y
    if extra:
        avail -= 230
    f, lines, size = fit(d, text, "SemiBold", CWID, avail, 68, 40, 1.3)
    y = draw_lines(d, lines, f, size, X0, y, TXT, 1.3) + 40
    if extra:
        lab, val = extra
        d.text((X0, y), lab, font=font("ExtraBold", 40), fill=MUT)
        f, lines, size = fit(d, val, "Regular", CWID, Y_CONTENT_END - y - 60, 44, 32, 1.3)
        draw_lines(d, lines, f, size, X0, y + 60, (205, 212, 225), 1.3)
    return img


def slide_list(label, items, seed):
    img = background(seed)
    d = ImageDraw.Draw(img)
    header(img, d)
    y = Y0 + 170
    d.rounded_rectangle([X0, y + 8, X0 + 12, y + 92], radius=6, fill=ACC)
    d.text((X0 + 36, y), label, font=font("ExtraBold", 84), fill=(167, 139, 250))
    y += 160
    items = [str(i) for i in items if str(i).strip()][:4]
    per = (Y_CONTENT_END - y) / max(len(items), 1)
    for i, it in enumerate(items):
        f, lines, size = fit(d, it, "SemiBold", CWID - 110, per - 34, 54, 34, 1.25)
        d.ellipse([X0, y + 4, X0 + 72, y + 76], fill=ACC)
        nf = font("ExtraBold", 40)
        n = str(i + 1)
        d.text((X0 + 36 - d.textlength(n, font=nf) / 2, y + 14), n, font=nf, fill="white")
        draw_lines(d, lines, f, size, X0 + 110, y + 6, TXT, 1.25)
        y += per
    return img


def slide_end(p, seed):
    img = background(seed)
    d = ImageDraw.Draw(img)
    cx = CW // 2
    lg = logo(260)
    img.alpha_composite(lg, (cx - 130, 300))
    def center(text, y, f, fill):
        d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)
    center("Git Hunter", 610, font("ExtraBold", 110), TXT)
    center("Каждый день — интересные", 770, font("SemiBold", 50), MUT)
    center("проекты GitHub простыми словами", 835, font("SemiBold", 50), MUT)
    uf = font("ExtraBold", 50)
    tw = d.textlength(SITE_SHORT, font=uf)
    d.rounded_rectangle([cx - tw / 2 - 40, 950, cx + tw / 2 + 40, 1050], radius=50, fill=ACC)
    center(SITE_SHORT, 972, uf, "white")
    center("Ссылка на проект — в описании", 1100, font("SemiBold", 44), ACC2)
    center(p["full_name"], 1165, font("Regular", 38), MUT)
    return img


def subtitle_png(text, path):
    tmp = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    f = font("ExtraBold", 66)
    lines = wrap(d, text, f, W - 180)
    if len(lines) > 2:
        f = font("ExtraBold", 56)
        lines = wrap(d, text, f, W - 160)[:3]
    size = f.size
    lh = int(size * 1.22)
    bw = max(d.textlength(l, font=f) for l in lines) + 70
    bh = lh * len(lines) + 44
    im = Image.new("RGBA", (W, int(bh) + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([(W - bw) / 2, 0, (W + bw) / 2, bh], radius=28, fill=(8, 10, 18, 205))
    y = 20
    for l in lines:
        tw = d.textlength(l, font=f)
        d.text(((W - tw) / 2, y), l, font=f, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
        y += lh
    im.save(path)
    return im.height


# ------------------------------------------------------------------ звук и тайминги
async def _tts(text, mp3):
    import edge_tts
    words, buf = [], bytearray()
    comm = edge_tts.Communicate(text, VOICE, rate="+5%", boundary="WordBoundary")
    async for ch in comm.stream():
        if ch["type"] == "audio":
            buf.extend(ch["data"])
        elif ch["type"] == "WordBoundary":
            words.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    if len(buf) < 5000 or not words:
        raise RuntimeError("пустой ответ edge-tts")
    Path(mp3).write_bytes(bytes(buf))
    return words


def tts_with_words(text, mp3):
    for attempt in range(4):
        try:
            return asyncio.run(_tts(text, mp3))
        except Exception as e:  # noqa
            log("edge-tts:", e)
            import time
            time.sleep(4 * (attempt + 1))
    return None


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def chunks_from_words(words, text):
    """Группируем слова в фразы по 2-5 слов; знаки препинания берём из исходного текста."""
    tokens = text.split()
    ti = 0
    res, cur, start = [], [], None
    for (a, b, w) in words:
        # находим токен с пунктуацией, соответствующий слову
        tok = w
        for j in range(ti, min(ti + 4, len(tokens))):
            if re.sub(r"\W", "", tokens[j]).lower().startswith(re.sub(r"\W", "", w).lower()[:3] or "§"):
                tok, ti = tokens[j], j + 1
                break
        if start is None:
            start = a
        cur.append(tok)
        txt = " ".join(cur)
        if len(cur) >= 5 or len(txt) > 30 or re.search(r"[.!?,:;—]$", tok):
            res.append([start, b, txt])
            cur, start = [], None
    if cur:
        res.append([start, words[-1][1], " ".join(cur)])
    for i in range(len(res) - 1):  # без «мигания» между фразами
        res[i][1] = max(res[i][1], min(res[i + 1][0], res[i][1] + 0.4))
    return res


def chunks_proportional(text, dur):
    parts, cur = [], []
    for t in text.split():
        cur.append(t)
        if len(cur) >= 4 or len(" ".join(cur)) > 28 or re.search(r"[.!?,:;]$", t):
            parts.append(" ".join(cur))
            cur = []
    if cur:
        parts.append(" ".join(cur))
    total = sum(len(p) + 3 for p in parts)
    t, res = 0.0, []
    for p in parts:
        d = dur * (len(p) + 3) / total
        res.append([t, t + d, p])
        t += d
    return res


# ------------------------------------------------------------------ тексты постов
def hashtags(p):
    tags = ["#GitHunter", "#github", "#opensource", "#программирование", "#полезное"]
    cat_tags = {"ai": ["#ИИ", "#нейросети", "#AI"], "devtools": ["#разработка", "#devtools"],
                "automation": ["#автоматизация"], "bots": ["#телеграм", "#боты"], "web": ["#вебразработка"],
                "selfhosted": ["#selfhosted"], "mobile": ["#android", "#приложения"], "media": ["#видео", "#контент"],
                "security": ["#безопасность"]}
    tags += cat_tags.get(p.get("category"), [])
    if p.get("language"):
        tags.append("#" + re.sub(r"[^\w]", "", p["language"]).lower())
    seen, out = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def make_post(p, video_url=""):
    s = p["summary"]
    tags = hashtags(p)
    title = f"{p['name']}: {s.get('tagline', '')}".strip(": ")
    if len(title) > 88:
        title = title[:87].rsplit(" ", 1)[0].rstrip(",.:;—-") + "…"
    yt_title = f"{title} #shorts"
    feats = "\n".join(f"• {f}" for f in (s.get("features") or [])[:5])
    yt_desc = (f"{s.get('tagline', '')}\n\n"
               f"Что это: {s.get('what', '')}\n\n"
               f"Зачем: {s.get('why', '')}\n\n"
               + (f"Что умеет:\n{feats}\n\n" if feats else "")
               + f"Как начать: {s.get('how_to_start', '')}\n\n"
               f"🔗 Проект на GitHub: {p['url']}\n"
               f"🔎 Ежедневная подборка Git Hunter: {SITE}#/p/{p['full_name']}\n\n"
               f"⭐ {p['stars']} · {p.get('language') or ''}\n\n" + " ".join(tags + ["#shorts"]))[:4900]
    caption = (f"🔥 {p['name']} — {s.get('tagline', '')}\n\n"
               f"{s.get('what', '')}\n\n"
               f"Зачем: {s.get('why', '')}\n\n"
               f"🔗 github.com/{p['full_name']}\n"
               f"Больше проектов каждый день — ссылка в профиле 👉 Git Hunter\n\n" + " ".join(tags))
    if len(caption) > 2150:  # лимит Instagram 2200, TikTok 2200
        caption = caption[:2000].rsplit(" ", 1)[0] + "…\n\n" + " ".join(tags)
    return {"youtube_title": yt_title[:100], "youtube_description": yt_desc, "caption": caption,
            "hashtags": tags}


# ------------------------------------------------------------------ сборка видео
TRANSITIONS = ["fade", "smoothleft", "smoothup", "fade", "slideleft", "fadeblack"]


def build_video(p, work, out_mp4, audio_mp3):
    s = p["summary"]
    narration = f"{p['name']}. {s.get('narration', '')}"
    words = tts_with_words(narration, audio_mp3)
    if not audio_mp3.exists():
        raise RuntimeError("нет аудио")
    adur = duration(audio_mp3)
    tempo = 1.0
    if adur + LEAD + END_CARD * 0.5 > MAX_LEN:
        tempo = (adur + LEAD + END_CARD * 0.5) / MAX_LEN
    spoken = adur / tempo
    chunks = chunks_from_words(words, narration) if words else chunks_proportional(narration, adur)
    log(f"  аудио {adur:.1f}s, слов-таймингов: {len(words or [])}, фраз: {len(chunks)}, темп {tempo:.2f}")

    pic = load_image([p.get("readme_image"), p.get("image")]) if p.get("readme_image") else load_image([p.get("image")])
    slides = [slide_title(p, pic, 0), slide_text("Что это", s.get("what", p.get("description", "")), 1)]
    if s.get("why"):
        slides.append(slide_text("Зачем", s["why"], 2, accent=(52, 211, 153)))
    if s.get("features"):
        slides.append(slide_list("Что умеет", s["features"], 3))
    if s.get("how_to_start"):
        slides.append(slide_text("Как начать", s["how_to_start"], 4,
                                 extra=("Кому пригодится", s["who"]) if s.get("who") else None, accent=(251, 191, 36)))
    slides.append(slide_end(p, 5))

    total = LEAD + spoken + 0.8 + END_CARD * 0.6
    total = min(max(total, 15), MAX_LEN + 1)
    n = len(slides)
    content_time = total - END_CARD + (n - 1) * TRANS  # сумма длительностей всех слайдов кроме финального
    weights = [1.25, 1.2, 1.1, 1.2, 1.0][: n - 1]
    durs = [content_time * w / sum(weights) for w in weights] + [END_CARD + TRANS]
    # фактическая длительность = sum(durs) - (n-1)*TRANS = total

    inputs, filters = [], []
    for i, (im, d) in enumerate(zip(slides, durs)):
        path = work / f"slide{i}.png"
        im.convert("RGB").save(path)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", str(path)]
        dx, dy = (PAN_X, PAN_Y) if i % 2 == 0 else (0, 0)
        sx, sy = ("+", "+") if i % 2 == 0 else ("-", "-")
        xe = f"{PAN_X if i % 2 else 0}{'-' if i % 2 else '+'}{PAN_X}*t/{d:.3f}"
        ye = f"{PAN_Y if i % 2 else 0}{'-' if i % 2 else '+'}{PAN_Y}*t/{d:.3f}"
        filters.append(f"[{i}:v]crop={W}:{H}:x='{xe}':y='{ye}',setsar=1,format=yuv420p,fps={FPS}[v{i}]")
    prev, acc = "v0", 0.0
    for i in range(1, n):
        acc += durs[i - 1] - TRANS
        out = f"x{i}"
        filters.append(f"[{prev}][v{i}]xfade=transition={TRANSITIONS[(i - 1) % len(TRANSITIONS)]}:duration={TRANS}:offset={acc:.3f}[{out}]")
        prev = out

    # субтитры
    sub_idx = n + 1  # n слайдов + аудио
    for k, (a, b, txt) in enumerate(chunks):
        sp = work / f"sub{k}.png"
        sh = subtitle_png(txt, sp)
        inputs += ["-i", str(sp)]
        ta, tb = LEAD + a / tempo, LEAD + b / tempo
        y = SUB_Y - sh // 2
        out = f"s{k}"
        filters.append(f"[{prev}][{sub_idx + k}:v]overlay=0:{y}:enable='between(t,{ta:.2f},{tb:.2f})'[{out}]")
        prev = out
    af = f"[{n}:a]atempo={tempo:.4f},adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad[aout]" if tempo != 1.0 else \
        f"[{n}:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad[aout]"
    filters.append(af)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs[: n * 8], "-i", str(audio_mp3), *inputs[n * 8:],
           "-filter_complex", ";".join(filters), "-map", f"[{prev}]", "-map", "[aout]",
           "-t", f"{total:.2f}", "-r", str(FPS),
           "-c:v", "libx264", "-preset", "medium", "-crf", "27", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-movflags", "+faststart", str(out_mp4)]
    (work / "cmd.txt").write_text(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr[-1500:])
    slides[0].convert("RGB").crop((PAN_X // 2, PAN_Y // 2, PAN_X // 2 + W, PAN_Y // 2 + H)).resize((540, 960)).save(
        out_mp4.with_suffix(".jpg"), quality=82)
    return total, bool(words)


# ------------------------------------------------------------------ release
def gh(*args, check=True):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def upload_release(date, files):
    tag = f"digest-{date}"
    if gh("release", "view", tag, "-R", REPO, check=False).returncode != 0:
        gh("release", "create", tag, "-R", REPO, "--title", f"Git Hunter — видео за {date}",
           "--notes", f"Вертикальные видео (1080×1920) для подборки за {date}: {SITE}#/day/{date}", "--latest=false")
    for i in range(0, len(files), 6):
        gh("release", "upload", tag, "-R", REPO, "--clobber", *[str(f) for f in files[i:i + 6]])
    return f"https://github.com/{REPO}/releases/download/{tag}/"


def main():
    index = json.loads((ROOT / "data/index.json").read_text(encoding="utf-8"))
    if not index["days"]:
        log("нет подборок")
        return
    date = os.environ.get("VIDEO_DATE") or index["days"][0]["date"]
    day_path = ROOT / f"data/{date}.json"
    day = json.loads(day_path.read_text(encoding="utf-8"))
    force = os.environ.get("VIDEO_FORCE") == "1"
    limit = int(os.environ.get("VIDEO_LIMIT") or 0)
    vdir = ROOT / "video"
    vdir.mkdir(exist_ok=True)
    made, stats = [], {"video": 0, "synced": 0, "failed": 0}
    todo = day["projects"][:limit] if limit else day["projects"]
    for p in todo:
        slug = re.sub(r"[^a-z0-9]+", "-", p["full_name"].lower()).strip("-")
        name = f"{date}-{slug}.mp4"
        out = vdir / name
        if p.get("video") and not force:
            p.setdefault("post", make_post(p))
            continue
        log(f"видео: {p['full_name']}")
        audio_rel = p.get("audio") or f"audio/{date}-{slug}.mp3"
        with tempfile.TemporaryDirectory() as td:
            try:
                total, synced = build_video(p, Path(td), out, ROOT / audio_rel)
            except Exception as e:  # noqa
                log("  ОШИБКА:", e)
                stats["failed"] += 1
                p["post"] = make_post(p)
                continue
        mb = out.stat().st_size / 1e6
        log(f"  готово: {total:.1f}s, {mb:.1f} MB")
        p["audio"] = audio_rel
        p["video"] = f"video/{name}"
        p["video_duration"] = round(total, 1)
        p["video_mb"] = round(mb, 1)
        p["video_synced_subs"] = synced
        p["post"] = make_post(p)
        made += [out, out.with_suffix(".jpg")]
        stats["video"] += 1
        stats["synced"] += int(synced)
    if made and os.environ.get("NO_RELEASE") != "1":
        base = upload_release(date, made)
        for p in day["projects"]:
            if p.get("video"):
                p["video_release_url"] = base + Path(p["video"]).name
                p["video_poster_release_url"] = base + Path(p["video"]).with_suffix(".jpg").name
    day_path.write_text(json.dumps(day, ensure_ascii=False, indent=1), encoding="utf-8")
    # синхронизируем projects.json
    pj = ROOT / "data/projects.json"
    projects = json.loads(pj.read_text(encoding="utf-8"))
    by = {(p["date"], p["full_name"]): p for p in day["projects"]}
    projects = [by.get((p["date"], p["full_name"]), p) for p in projects]
    pj.write_text(json.dumps(projects, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"Видео: {stats}")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"\n\n### Видео за {date}\nСобрано: {stats['video']}, с синхронными субтитрами: {stats['synced']}, ошибок: {stats['failed']}\n")


if __name__ == "__main__":
    main()
