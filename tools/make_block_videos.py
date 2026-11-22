#!/usr/bin/env python3
"""Git Hunter Studio: вертикальное видео 1080x1920 на каждый блок (по движку Git Hunter: Кен Бёрнс, переходы, синхронные субтитры)."""
import json, sys, subprocess, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import video_lib as V
from video_lib import (Image, ImageDraw, ImageFilter, background, header, fit, draw_lines, font, logo, rounded, contain,
                       slide_text, slide_list, subtitle_png, chunks_from_words, duration, TRANSITIONS,
                       W, H, CW, CH, PAN_X, PAN_Y, FPS, TRANS, END_CARD, LEAD, SUB_Y, X0, X1, CWID, Y0, Y_CONTENT_END, TXT, MUT, ACC, ACC2)
ROOT = Path(__file__).resolve().parent.parent
SITE = "https://avtomaster24bot-lab.github.io/git-hunter-studio/"
SITE_SHORT = "avtomaster24bot-lab.github.io/git-hunter-studio"
TG = "https://t.me/Git_Hunter_bot?start=consult"
REPO = "avtomaster24bot-lab/git-hunter-studio"; TAG = "studio-videos-v1"

def slide_cover(c, num, pic, seed):
    img = background(seed); d = ImageDraw.Draw(img)
    header(img, d, c["badge"])
    y = Y0 + 120
    ph = int(CWID / 2)
    im = rounded(contain(pic, CWID, ph))
    sh = Image.new("RGBA", (CWID + 60, ph + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([30, 40, CWID + 30, ph + 30], radius=30, fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (X0 - 30, y - 30)); img.alpha_composite(im, (X0, y))
    y += ph + 60
    d.text((X0, y), f"{num:02d} / 10", font=font("SemiBold", 34), fill=ACC2); y += 64
    f, lines, size = fit(d, c["title"], "ExtraBold", CWID, 260, 100, 56, 1.1)
    y = draw_lines(d, lines, f, size, X0, y, TXT, 1.1) + 24
    f, lines, size = fit(d, c["tagline"], "SemiBold", CWID, Y_CONTENT_END - y, 56, 36, 1.25)
    draw_lines(d, lines, f, size, X0, y, (196, 181, 253), 1.25)
    return img

def slide_feature(text, i, n, seed):
    img = background(seed); d = ImageDraw.Draw(img); header(img, d, f"Что умеет · {i}/{n}")
    y = Y0 + 200
    cx = X0 + 90
    d.ellipse([X0, y, X0 + 180, y + 180], fill=ACC)
    nf = font("ExtraBold", 100); d.text((cx - d.textlength(str(i), font=nf) / 2, y + 30), str(i), font=nf, fill="white")
    y += 260
    f, lines, size = fit(d, text, "ExtraBold", CWID, Y_CONTENT_END - y, 84, 48, 1.22)
    draw_lines(d, lines, f, size, X0, y, TXT, 1.22)
    return img

def slide_end(seed):
    img = background(seed); d = ImageDraw.Draw(img); cx = CW // 2
    img.alpha_composite(logo(230), (cx - 115, 280))
    def center(t, y, f, fill): d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)
    center("Git Hunter Studio", 560, font("ExtraBold", 92), TXT)
    center("Бесплатная консультация", 700, font("SemiBold", 54), MUT)
    center("15 минут · без обязательств", 770, font("SemiBold", 46), MUT)
    uf = font("ExtraBold", 58); t = "@Git_Hunter_bot"; tw = d.textlength(t, font=uf)
    d.rounded_rectangle([cx - tw / 2 - 50, 880, cx + tw / 2 + 50, 990], radius=55, fill=ACC); center(t, 904, uf, "white")
    center("Сайт:", 1060, font("SemiBold", 38), ACC2)
    sf = font("SemiBold", 34); center(SITE_SHORT, 1112, sf, TXT)
    return img

def build(b, c, num, out_mp4):
    audio = ROOT / f"audio/{b['id']}.mp3"
    words = json.load(open(ROOT / f"tools/words/{b['id']}.json"))
    adur = duration(audio)
    chunks = chunks_from_words(words, b["text"])
    pic = Image.open(ROOT / f"img/{b['id']}.jpg").convert("RGB")
    feats = c["features"]
    slides = [slide_cover(c, num, pic, 0), slide_text("Что это", c["what"], 1), slide_text("Зачем вам", c["why"], 2, accent=(52, 211, 153))]
    if len(feats) <= 3:
        slides += [slide_feature(f, i + 1, len(feats), 3 + i) for i, f in enumerate(feats)]
    else:
        import math, re as _re
        clean = [_re.sub(r"[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F]", "", f).strip() for f in feats]
        per = math.ceil(len(clean) / math.ceil(len(clean) / 3))
        for k in range(0, len(clean), per):
            slides.append(slide_list("Что умеет", clean[k:k + per], 3 + k))
    tail = ("Цена", c["price"]) if c.get("price") else ("Дальше", c.get("next", "")) if c.get("next") else None
    slides.append(slide_text("Для кого", c["who"], 6, extra=tail, accent=(251, 191, 36)))
    slides.append(slide_end(7))
    total = LEAD + adur + 0.6 + END_CARD * 0.6
    n = len(slides)
    content_time = total - END_CARD + (n - 1) * TRANS
    weights = [1.3] + [1.0] * (n - 2)
    durs = [content_time * w / sum(weights) for w in weights] + [END_CARD + TRANS]
    with tempfile.TemporaryDirectory() as td:
        work = Path(td); inputs, filters = [], []
        for i, (im, dd) in enumerate(zip(slides, durs)):
            pth = work / f"slide{i}.png"; im.convert("RGB").save(pth)
            inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dd:.3f}", "-i", str(pth)]
            xe = f"{PAN_X if i % 2 else 0}{'-' if i % 2 else '+'}{PAN_X}*t/{dd:.3f}"
            ye = f"{PAN_Y if i % 2 else 0}{'-' if i % 2 else '+'}{PAN_Y}*t/{dd:.3f}"
            filters.append(f"[{i}:v]crop={W}:{H}:x='{xe}':y='{ye}',setsar=1,format=yuv420p,fps={FPS}[v{i}]")
        prev, acc = "v0", 0.0
        for i in range(1, n):
            acc += durs[i - 1] - TRANS
            filters.append(f"[{prev}][v{i}]xfade=transition={TRANSITIONS[(i - 1) % len(TRANSITIONS)]}:duration={TRANS}:offset={acc:.3f}[x{i}]"); prev = f"x{i}"
        sub_inputs = []
        for k, (a, bb, txt) in enumerate(chunks):
            sp = work / f"sub{k}.png"; sh = subtitle_png(txt, sp); sub_inputs += ["-i", str(sp)]
            filters.append(f"[{prev}][{n + 1 + k}:v]overlay=0:{SUB_Y - sh // 2}:enable='between(t,{LEAD + a:.2f},{LEAD + bb:.2f})'[s{k}]"); prev = f"s{k}"
        filters.append(f"[{n}:a]adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad[aout]")
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-i", str(audio), *sub_inputs,
               "-filter_complex", ";".join(filters), "-map", f"[{prev}]", "-map", "[aout]", "-t", f"{total:.2f}", "-r", str(FPS),
               "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-profile:v", "high", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-movflags", "+faststart", str(out_mp4)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode: raise RuntimeError(r.stderr[-1500:])
        slides[0].convert("RGB").crop((PAN_X // 2, PAN_Y // 2, PAN_X // 2 + W, PAN_Y // 2 + H)).resize((540, 960)).save(out_mp4.with_suffix(".jpg"), quality=82)
    return round(total, 1), n, len(chunks)

TAGS = {"03-assistant": ["#ИИассистент", "#личныйассистент"], "04-site": ["#сайтподключ", "#личныйбренд", "#сайтдлябизнеса"],
        "05-automation": ["#автоматизация", "#чатбот", "#CRM", "#контентзавод"], "06-niches": ["#автосервис", "#салонкрасоты", "#стоматология", "#недвижимость"],
        "07-prices": ["#цены", "#тенге"], "02-trust": ["#GitHunter", "#opensource"]}
def make_post(b, c):
    tags = ["#GitHunterStudio", "#ИИдлябизнеса", "#нейросети", "#автоматизация", "#бизнесказахстан", "#алматы", "#астана"] + TAGS.get(b["id"], [])
    tags = list(dict.fromkeys(tags))
    feats = "\n".join(f"• {f}" for f in c["features"])
    tail = c.get("price") or c.get("next", "")
    title = f"{c['title']}: {c['tagline']}"
    if len(title) > 88: title = title[:87].rsplit(" ", 1)[0].rstrip(",.:;—-") + "…"
    yt_desc = (f"{c['tagline']}\n\nЧто это: {c['what']}\n\nЗачем вам: {c['why']}\n\nЧто умеет:\n{feats}\n\nДля кого: {c['who']}\n\n{tail}\n\n"
               f"💬 Бесплатная консультация: {TG}\n🌐 Сайт: {SITE}\n📢 Канал: https://t.me/githunter77\n\n" + " ".join(tags + ["#shorts"]))
    cap = (f"🔥 {c['title']} — {c['tagline']}\n\n{c['what']}\n\nЗачем вам: {c['why']}\n\n{feats}\n\n{tail}\n\n"
           f"💬 Бесплатная консультация — @Git_Hunter_bot (ссылка в профиле)\n\n" + " ".join(tags))
    tt = (f"{c['title']} — {c['tagline']} 🔥\n{c['why']}\n💬 Консультация бесплатно — @Git_Hunter_bot\n\n" + " ".join(tags[:8] + ["#fyp", "#рекомендации"]))
    return {"youtube_title": (title + " #shorts")[:100], "youtube_description": yt_desc[:4900], "instagram": cap[:2150], "tiktok": tt[:2150]}

def main():
    B = json.load(open(ROOT / "tools/blocks.json")); C = json.load(open(ROOT / "tools/cards.json"))
    only = sys.argv[1:]
    (ROOT / "video").mkdir(exist_ok=True)
    out = []
    for num, b in enumerate(B, 1):
        c = C[b["id"]]
        item = {**b, **c, "num": num, "image": f"img/{b['id']}.jpg", "audio": f"audio/{b['id']}.mp3", "post": make_post(b, c)}
        mp4 = ROOT / f"video/{b['id']}.mp4"
        if (not only or b["id"] in only) and (ROOT / f"tools/words/{b['id']}.json").exists():
            total, ns, nc = build(b, c, num, mp4); print(b["id"], total, "s", ns, "slides", nc, "subs", flush=True)
            item.update(video_duration=total, slides=ns)
        elif mp4.exists():
            prev = {x["id"]: x for x in json.load(open(ROOT / "data/cards.json"))} if (ROOT / "data/cards.json").exists() else {}
            item.update({k: prev.get(b["id"], {}).get(k) for k in ("video_duration", "slides")})
        if mp4.exists():
            item.update(video=f"video/{b['id']}.mp4", poster=f"video/{b['id']}.jpg", video_mb=round(mp4.stat().st_size / 1e6, 1),
                        video_release_url=f"https://github.com/{REPO}/releases/download/{TAG}/{b['id']}.mp4")
        out.append(item)
    (ROOT / "data").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "data/cards.json", "w"), ensure_ascii=False, indent=1)
main()
