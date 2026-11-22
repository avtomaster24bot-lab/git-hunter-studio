# Git Hunter Studio — лендинг с аудио

**Сайт:** https://avtomaster24bot-lab.github.io/git-hunter-studio/

Продающий лендинг: личный ИИ-ассистент, сайты с ИИ-консультантом, ИИ-автоматизация бизнеса (Казахстан, цены в ₸).
Принцип — «читать минимум»: каждый блок = короткий заголовок + кнопка **«Послушайте аудио»** + кнопка **«Текст аудио»**. 10 аудио, проигрываются по очереди.

Заявки: кнопки ведут в https://t.me/Git_Hunter_bot?start=consult. Форма собирает имя, контакт и что нужно, копирует текст и открывает бота (токены во фронтенде не используются).

## Промо-материалы (папка `promo/`)
- Посты с хэштегами: [promo/POSTS.md](promo/POSTS.md)
- Вертикальные видео 1080×1920 (Release [promo-v1](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/tag/promo-v1)):
  - [promo-1-assistant.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-1-assistant.mp4) — ИИ-ассистент
  - [promo-2-site.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-2-site.mp4) — сайт с ИИ-консультантом
  - [promo-3-prices.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-3-prices.mp4) — пакеты и цены

## Как менять
- Тексты блоков и озвучки: `tools/blocks.json` → `python3 tools/tts.py` (удалите старый mp3) → `python3 tools/build.py`
- Дизайн: `style.css`, логика плеера и формы: `app.js`
- Промо: `promo/src/promos.json` → `python3 promo/src/tts_promo.py && python3 promo/src/render.py`
