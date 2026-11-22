# Git Hunter Studio — сайт услуг в формате Git Hunter

**Сайт:** https://avtomaster24bot-lab.github.io/git-hunter-studio/

Продающий сайт: личный ИИ-ассистент, сайты с ИИ-консультантом, ИИ-автоматизация бизнеса (Казахстан, цены в ₸).
Оформлен как карточки ежедневной подборки [Git Hunter](https://avtomaster24bot-lab.github.io/git-hunter/): у каждой из 10 карточек есть
картинка, название, короткое описание, разделы «Что это / Зачем вам / Что умеет / Для кого / Цена», аудио-рассказ, вертикальное видео прямо в карточке,
кнопки «⬇ Скачать видео», «📋 Текст для YouTube / Instagram / TikTok», «Текст аудио», «Поделиться».
Плюс плеер «слушать всё подряд», галерея Shorts, пакеты и цены, форма заявки и закреплённая кнопка консультации.

Заявки: https://t.me/Git_Hunter_bot?start=consult. Форма копирует текст заявки и открывает бота (токенов во фронтенде нет).

## Видео
- 10 видео услуг (1080×1920, 7–8 слайдов, Кен Бёрнс, переходы, субтитры по словам): папка `video/` на сайте и Release [studio-videos-v1](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/tag/studio-videos-v1)
- 3 промо-видео: Release [promo-v1](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/tag/promo-v1) —
  [promo-1-assistant.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-1-assistant.mp4), [promo-2-site.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-2-site.mp4), [promo-3-prices.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-3-prices.mp4)
- Посты с хэштегами: [promo/POSTS.md](promo/POSTS.md); тексты для каждой карточки — в `data/cards.json` (поле `post`) и по кнопкам на сайте.

## Как менять
- Тексты озвучки: `tools/blocks.json`; разделы карточек: `tools/cards.json`
- Картинки: `python3 tools/pictures.py`
- Озвучка с таймингами слов: удалите `tools/words/<id>.json` → `python3 tools/tts_words.py`
- Видео и data/cards.json: `python3 tools/make_block_videos.py [id ...]`
