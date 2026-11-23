# Git Hunter Studio

**Сайт:** https://avtomaster24bot-lab.github.io/git-hunter-studio/

Продающий лендинг: личный ИИ-ассистент, сайты с ИИ-консультантом, ИИ-автоматизация бизнеса (Казахстан, цены в ₸).

Основная страница — как в первой версии: крупные кнопки «Плей», заголовок блока и переключатель «Текст аудио». Читать почти ничего не нужно. Когда одно аудио заканчивается, автоматически начинается следующее (и страница плавно прокручивается к нему).

В самом низу — свёрнутый компактный блок «Видео со слайдами»: 10 роликов услуг и 3 промо, с кнопкой «⬇ Скачать видео». Воспроизведение с сайта (`video/`), скачивание из релизов.

Заявки: https://t.me/Git_Hunter_bot?start=consult. Форма копирует текст заявки и открывает бота (токенов во фронтенде нет).

## Видео
- 10 видео услуг (1080×1920, 7–8 слайдов, Кен Бёрнс, переходы, субтитры по словам): папка `video/` на сайте и Release [studio-videos-v1](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/tag/studio-videos-v1)
- 3 промо-видео: Release [promo-v1](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/tag/promo-v1) —
  [promo-1-assistant.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-1-assistant.mp4), [promo-2-site.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-2-site.mp4), [promo-3-prices.mp4](https://github.com/avtomaster24bot-lab/git-hunter-studio/releases/download/promo-v1/promo-3-prices.mp4)
- Посты с хэштегами: [promo/POSTS.md](promo/POSTS.md); тексты постов для каждой услуги — в `data/cards.json` (поле `post`) и в `promo/POSTS.md`.

## Как менять
- Тексты озвучки: `tools/blocks.json`; разделы карточек: `tools/cards.json`
- Картинки: `python3 tools/pictures.py`
- Озвучка с таймингами слов: удалите `tools/words/<id>.json` → `python3 tools/tts_words.py`
- Видео и data/cards.json: `python3 tools/make_block_videos.py [id ...]`
