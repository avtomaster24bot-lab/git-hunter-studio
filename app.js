/* Git Hunter Studio — карточки услуг в формате Git Hunter */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const TG = "https://t.me/Git_Hunter_bot?start=consult";
  const PROMOS = [
    { v: "video/promo-1-assistant.mp4", t: "Промо: ИИ-ассистент" },
    { v: "video/promo-2-site.mp4", t: "Промо: сайт с ИИ-консультантом" },
    { v: "video/promo-3-prices.mp4", t: "Промо: пакеты и цены" },
  ];
  let cards = [], plIdx = -1;
  const toast = (t) => { const el = $("#toast"); el.textContent = t; el.classList.add("show"); clearTimeout(toast.t); toast.t = setTimeout(() => el.classList.remove("show"), 2200); };
  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); }
    catch (e) { const ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove(); }
  }
  const section = (t, x, cls = "") => (x ? `<div class="s"><b class="${cls}">${t}</b><p>${esc(x)}</p></div>` : "");

  function videoBlock(c) {
    if (!c.video) return "";
    return `<div class="vwrap">
      <video class="vplayer" controls playsinline preload="none" poster="${esc(c.poster)}" src="${esc(c.video)}"></video>
      <div class="vbtns">
        <a class="btn" href="${esc(c.video)}" download="${esc(c.id)}-git-hunter-studio.mp4">⬇ Скачать видео</a>
        <button class="btn ghost" data-copy="youtube" data-id="${esc(c.id)}">📋 Текст для YouTube</button>
        <button class="btn ghost" data-copy="instagram" data-id="${esc(c.id)}">📋 Для Instagram</button>
        <button class="btn ghost" data-copy="tiktok" data-id="${esc(c.id)}">📋 Для TikTok</button>
      </div><small class="vnote">Вертикальное видео 1080×1920${c.video_duration ? ` · ${Math.round(c.video_duration)} с` : ""}${c.slides ? ` · ${c.slides} слайдов` : ""}${c.video_mb ? ` · ${c.video_mb} МБ` : ""} — готово для Shorts, Reels и TikTok</small></div>`;
  }
  function card(c, i) {
    const tail = c.price ? section("Цена", c.price, "price") : section("Дальше", c.next);
    const links = (c.links || []).map(([t, u]) => `<a class="btn ghost" href="${esc(u)}" target="_blank" rel="noopener">${esc(t)} ↗</a>`).join("");
    return `<article class="card" id="b${c.num}" data-id="${esc(c.id)}">
      <a class="img" href="#b${c.num}"><img loading="lazy" src="${esc(c.image)}" alt="${esc(c.title)}">
        <span class="badge">${esc(c.emoji)} ${esc(c.badge)}</span><span class="rank">#${c.num}</span></a>
      <div class="body">
        <div class="title"><img class="ico" src="assets/logo.svg" alt=""><div><h3><a href="#b${c.num}">${esc(c.title)}</a></h3><small>Git Hunter Studio</small></div></div>
        <p class="tag">${esc(c.tagline)}</p>
        <div class="meta"><span>🎧 ${Math.round(c.dur)} с аудио</span>${c.video ? `<span class="hot">🎬 видео ${Math.round(c.video_duration || 0)} с</span>` : ""}<span>● ${c.features.length} пунктов</span></div>
        ${section("Что это", c.what)}${section("Зачем вам", c.why)}
        <div class="s"><b>Что умеет</b><ul>${c.features.map((f) => `<li>${esc(f)}</li>`).join("")}</ul></div>
        ${section("Для кого", c.who)}${tail}
        ${links ? `<div class="links">${links}</div>` : ""}
        ${videoBlock(c)}
        <details class="more tr"><summary>Текст аудио</summary><p>${esc(c.text)}</p></details>
        <div class="actions">
          <button class="btn" data-play="${i}">▶ Слушать</button>
          <a class="btn ghost" href="${TG}" target="_blank" rel="noopener">💬 Консультация</a>
          <button class="btn ghost" data-share="${c.num}" title="Поделиться">↗ Поделиться</button>
        </div>
      </div></article>`;
  }
  function render() {
    $("#cards").innerHTML = cards.map(card).join("");
    $("#quick").innerHTML = cards.map((c) => `<a href="#b${c.num}">${esc(c.emoji)} ${esc(c.badge)}</a>`).join("");
    const intro = cards[0];
    if (intro && intro.video) $("#heroVideo").innerHTML = `<video class="vplayer" controls playsinline preload="metadata" poster="${esc(intro.poster)}" src="${esc(intro.video)}"></video>`;
    const sh = cards.filter((c) => c.video).map((c) => ({ v: c.video, p: c.poster, t: `#${c.num} ${c.title}`, d: c.video_duration }))
      .concat(PROMOS.map((p) => ({ v: p.v, p: p.v.replace(/\.mp4$/, ".jpg"), t: p.t })));
    $("#shortsRow").innerHTML = sh.map((s) => `<div class="short"><video class="vplayer" controls playsinline preload="none" poster="${esc(s.p)}" src="${esc(s.v)}"></video>
      <b>${esc(s.t)}</b>${s.d ? `<small>${Math.round(s.d)} с · 1080×1920</small>` : `<small>1080×1920</small>`}<a class="btn ghost" href="${esc(s.v)}" download>⬇ Скачать видео</a></div>`).join("");
    if (location.hash.startsWith("#b")) setTimeout(() => document.getElementById(location.hash.slice(1))?.scrollIntoView(), 50);
  }
  function postText(c, kind) {
    const p = c.post || {};
    return kind === "youtube" ? `${p.youtube_title}\n\n${p.youtube_description}` : p[kind] || "";
  }

  /* ---------- плеер «подкаст» ---------- */
  const A = $("#plAudio");
  function play(i) {
    if (i < 0 || i >= cards.length) return;
    plIdx = i; const c = cards[i];
    document.querySelectorAll("video").forEach((v) => v.pause());
    A.src = c.audio; A.play().catch(() => {});
    $("#plTitle").textContent = `${c.num}. ${c.title}`; $("#plSub").textContent = `${i + 1} из ${cards.length} · Git Hunter Studio`;
    $("#player").classList.remove("hidden"); document.body.classList.add("pl-on");
    document.querySelectorAll(".card").forEach((el) => el.classList.toggle("playing", el.dataset.id === c.id));
  }
  A.onended = () => play(plIdx + 1);
  $("#plPrev").onclick = () => play(Math.max(0, plIdx - 1));
  $("#plNext").onclick = () => play(plIdx + 1);
  $("#plClose").onclick = () => { A.pause(); $("#player").classList.add("hidden"); document.body.classList.remove("pl-on"); document.querySelectorAll(".card.playing").forEach((e) => e.classList.remove("playing")); };
  $("#playAll").onclick = () => play(0);
  document.addEventListener("play", (e) => { if (e.target.tagName === "VIDEO") { A.pause(); document.querySelectorAll("video").forEach((v) => v !== e.target && v.pause()); } }, true);

  document.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-play],[data-copy],[data-share]"); if (!b) return;
    const d = b.dataset;
    if (d.play) play(+d.play);
    else if (d.copy) { const c = cards.find((x) => x.id === d.id); if (c) { await copyText(postText(c, d.copy)); toast({ youtube: "Название и описание для YouTube скопированы", instagram: "Подпись для Instagram скопирована", tiktok: "Подпись для TikTok скопирована" }[d.copy]); } }
    else if (d.share) {
      const url = location.origin + location.pathname + "#b" + d.share;
      if (navigator.share) navigator.share({ title: "Git Hunter Studio", url }).catch(() => {}); else { await copyText(url); toast("Ссылка скопирована"); }
    }
  });

  /* ---------- заявка ---------- */
  const f = $("#leadForm");
  f.querySelectorAll(".pick .chip").forEach((b) => (b.onclick = () => b.classList.toggle("sel")));
  const res = f.querySelector(".result"), pre = res.querySelector("pre");
  f.onsubmit = (e) => {
    e.preventDefault(); const fd = new FormData(f);
    const need = [...f.querySelectorAll(".pick .sel")].map((b) => b.textContent).join(", ") || "—";
    const msg = `Здравствуйте! Хочу бесплатную консультацию.\nИмя: ${fd.get("name")}\nКонтакт: ${fd.get("contact")}\nЧто нужно: ${need}`;
    pre.textContent = msg; res.hidden = false; copyText(msg); window.open(TG, "_blank", "noopener");
  };
  $("#copyLead").onclick = async () => { await copyText(pre.textContent); toast("Скопировано ✓"); };

  fetch("data/cards.json", { cache: "no-cache" }).then((r) => r.json()).then((d) => { cards = d; render(); })
    .catch(() => ($("#cards").innerHTML = `<div class="empty">Не удалось загрузить карточки. Обновите страницу.</div>`));
})();
