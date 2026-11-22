import json, html
B=json.load(open('tools/blocks.json'))
URL="https://avtomaster24bot-lab.github.io/git-hunter-studio/"
TG="https://t.me/Git_Hunter_bot?start=consult"
def fmt(s): s=int(round(s)); return f"{s//60}:{s%60:02d}"
def player(b,n):
    return f'''<div class="player" data-src="audio/{b['id']}.mp3">
  <button class="play" aria-label="Послушайте аудио"><span class="ring"><svg viewBox="0 0 120 120"><circle class="bg" cx="60" cy="60" r="54"/><circle class="fg" cx="60" cy="60" r="54"/></svg></span>
  <span class="ico"><svg class="i-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg><svg class="i-pause" viewBox="0 0 24 24"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg></span></button>
  <div class="pmeta"><div class="plabel">Послушайте аудио <span class="num">{n:02d}</span></div>
  <div class="bar"><div class="fill"></div></div><div class="time"><span class="cur">0:00</span> / <span>{fmt(b['dur'])}</span></div></div>
</div>
<button class="ttoggle" aria-expanded="false">Текст аудио</button>
<div class="transcript"><p>{html.escape(b['text'])}</p></div>'''
extra={
"02-trust":'<div class="links"><a href="https://t.me/githunter77" target="_blank" rel="noopener">Канал Git Hunter ↗</a><a href="https://avtomaster24bot-lab.github.io/git-hunter/" target="_blank" rel="noopener">Сайт Git Hunter ↗</a></div>',
"03-assistant":'<div class="chips static"><span>📧 Почта</span><span>💬 WhatsApp · Telegram · Instagram</span><span>🎬 Контент</span><span>📅 Запись</span><span>📊 Отчёты и КП</span><span>🔒 Данные у вас</span></div>',
"04-site":'<div class="chips static"><span>⚡ 3–7 дней</span><span>📱 Mobile-first</span><span>🤖 ИИ-консультант 24/7</span></div>',
"05-automation":'<div class="chips static"><span>🗓 Бот записи</span><span>💸 Бот продаж</span><span>💬 Автоответы</span><span>📇 CRM</span><span>🏭 Контент-завод → YouTube · TikTok · Instagram</span></div>',
"06-niches":'<div class="niches"><span>🚗 Автосервис</span><span>💅 Салон красоты</span><span>🦷 Стоматология</span><span>🎓 Эксперт / коуч</span><span>🛍 Магазин</span><span>🏠 Недвижимость</span></div>',
"07-prices":'''<div class="cards">
<div class="card"><div class="cn">Старт</div><div class="cp">от 49 000 ₸</div><div class="cd">Ассистент + 1 канал</div></div>
<div class="card hot"><div class="badge">Популярный</div><div class="cn">Бизнес</div><div class="cp">от 149 000 ₸</div><div class="cd">Сайт + ИИ-консультант + бот + заявки</div></div>
<div class="card"><div class="cn">Под ключ</div><div class="cp">от 299 000 ₸</div><div class="cd">Всё + контент-завод + месяц поддержки</div></div>
<div class="card"><div class="cn">Поддержка</div><div class="cp">от 15 000 ₸<small>/мес</small></div><div class="cd">Обновления и новые навыки</div></div>
</div>''',
"08-process":'<ol class="steps"><li><b>1</b>Консультация 15 мин</li><li><b>2</b>Демо</li><li><b>3</b>Настройка</li><li><b>4</b>Обучение</li><li><b>5</b>Поддержка</li></ol>',
"09-faq":'<div class="chips static"><span>🔒 Безопасно</span><span>🙂 Просто</span><span>⏱ От нескольких дней</span><span>💻 Обычный ноутбук</span></div>',
}
secs=[]
for i,b in enumerate(B[1:],start=2):
    cta = '' 
    if b['id']=='10-final':
        cta=f'''<a class="btn big" href="{TG}" target="_blank" rel="noopener">Бесплатная консультация</a>
<form id="lead" class="lead" autocomplete="on">
 <div class="ftitle">Или оставьте заявку за 20 секунд</div>
 <input name="name" placeholder="Ваше имя" required maxlength="60">
 <input name="contact" placeholder="Телефон или @telegram" required maxlength="60">
 <div class="chips pick">
  <button type="button">ИИ-ассистент</button><button type="button">Сайт</button><button type="button">Бот / автоматизация</button><button type="button">Контент-завод</button><button type="button">Пока не знаю</button>
 </div>
 <button class="btn" type="submit">Отправить в Telegram</button>
 <div class="result" hidden><div class="rt">Текст скопирован — вставьте его в чат с ботом:</div><pre></pre><div class="ra"><button type="button" class="btn ghost copy">Скопировать</button><a class="btn" href="{TG}" target="_blank" rel="noopener">Открыть @Git_Hunter_bot</a></div></div>
</form>'''
    secs.append(f'''<section class="block reveal" id="b{i}">
<div class="tag">{i:02d} · {html.escape(b['tag'])}</div>
<h2>{html.escape(b['title'])}</h2>
{player(b,i)}
{extra.get(b['id'],'')}
{cta}
</section>''')
h=B[0]
page=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Git Hunter Studio — ИИ работает на вас, пока вы занимаетесь бизнесом</title>
<meta name="description" content="Личный ИИ-ассистент на вашем компьютере, сайты с ИИ-консультантом и автоматизация бизнеса в Казахстане. Послушайте — читать почти ничего не нужно.">
<meta name="theme-color" content="#07070c">
<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU">
<meta property="og:title" content="Git Hunter Studio — ИИ работает на вас">
<meta property="og:description" content="Личный ИИ-ассистент, сайты с ИИ-консультантом и автоматизация бизнеса. Бесплатная консультация 15 минут.">
<meta property="og:url" content="{URL}"><meta property="og:image" content="{URL}assets/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{URL}assets/og.png">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="assets/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head><body>
<div class="bgfx"><i></i><i></i><i></i></div>
<header class="top"><a class="brand" href="#"><span class="logo">GH</span> Git Hunter <b>Studio</b></a></header>
<main>
<section class="hero block" id="b1">
<div class="tag">01 · Git Hunter Studio</div>
<h1>ИИ работает <span class="grad">на вас</span>, пока вы занимаетесь бизнесом</h1>
<p class="sub">Читать не нужно — просто слушайте 🎧</p>
{player(h,1)}
<a class="scroll" href="#b2">Дальше ↓</a>
</section>
{''.join(secs)}
</main>
<footer>© 2026 Git Hunter Studio · Казахстан · <a href="https://t.me/githunter77" target="_blank" rel="noopener">@githunter77</a></footer>
<a class="sticky" href="{TG}" target="_blank" rel="noopener">💬 Бесплатная консультация</a>
<script src="app.js" defer></script>
</body></html>'''
open('index.html','w').write(page)
