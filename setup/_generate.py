#!/usr/bin/env python3
# Генерирует standalone-страницы разделов /setup/<id>/index.html из мастера /setup/index.html.
# Каждая страница — один раздел, без бокового меню и без других разделов в исходнике.
# Запуск: python3 setup/_generate.py   (из корня репо), затем git add setup/ && commit && push.
import re, os, html

HERE = os.path.dirname(os.path.abspath(__file__))          # .../setup
MASTER = os.path.join(HERE, "index.html")

BLOCKS = [
    ("prep", "01"), ("schedule", "02"), ("price", "03"), ("sales", "04"),
    ("clients", "05"), ("app", "06"), ("mkt-base", "07"), ("crm", "08"),
    ("mkt-adv", "09"), ("integrations", "10"),
]

src = open(MASTER, encoding="utf-8").read()
head = re.search(r"<head>.*?</head>", src, re.S).group(0)

STANDALONE_JS = r"""
<script>
const CHK='<span class="chk"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>';
document.querySelectorAll('.item').forEach(el=>el.insertAdjacentHTML('afterbegin',CHK));
const items=Array.from(document.querySelectorAll('.item'));
const STORE='__STORE__';
function save(){try{localStorage.setItem(STORE,JSON.stringify(items.map(e=>e.classList.contains('checked')?1:0)));}catch(e){}}
function load(){try{const r=localStorage.getItem(STORE);if(!r)return;const a=JSON.parse(r);items.forEach((e,i)=>{if(a[i])e.classList.add('checked');});}catch(e){}}
function upd(){
  const t=items.length,d=items.filter(e=>e.classList.contains('checked')).length,p=t?Math.round(d/t*100):0;
  const mp=document.getElementById('miniPct'); if(mp)mp.textContent=p+'%';
  const mini=document.getElementById('miniReady'); if(mini)mini.classList.toggle('done',p===100);
  const slot=document.querySelector('.role-foot-r');
  if(slot)slot.innerHTML=`<span class="role-progress"><span>${d}/${t}</span><span class="role-progress-bar"><span class="role-progress-fill" style="width:${p}%;"></span></span><span>${p}%</span></span>`;
}
document.querySelectorAll('.item').forEach(el=>el.addEventListener('click',e=>{if(e.target.closest('a'))return;el.classList.toggle('checked');save();upd();}));
load();upd();
</script>
"""

TEMPLATE = """<!doctype html>
<html lang="ru">
__HEAD__
<body class="with-links focus">

<div class="bar">
  <div class="bar-l">
    <div class="bar-logo">Fit<span>base</span></div>
    <div class="bar-sub">__BARSUB__</div>
  </div>
  <div class="bar-r">
    <div class="mini-ready" id="miniReady" title="Прогресс раздела"><span class="mini-ready-dot"></span><span class="mr-label">__MININUM__</span> <span id="miniPct">0%</span></div>
    <button class="print-btn" onclick="window.print()">Скачать PDF</button>
  </div>
</div>

<div class="book">
  <div class="content">
    <div class="focus-hint">Это отдельный шаг настройки. Отметьте выполненные пункты — прогресс сохранится в вашем браузере.</div>
    __SECTION__
  </div>
</div>
__JS__
</body>
</html>
"""

for bid, num in BLOCKS:
    m = re.search(r'<section class="page role view" id="%s">.*?</section>' % re.escape(bid), src, re.S)
    if not m:
        raise SystemExit("section not found: " + bid)
    section = m.group(0).replace('class="page role view"', 'class="page role view active"', 1)
    h2 = re.search(r"<h2>(.*?)</h2>", section, re.S).group(1)
    name = re.sub(r"<[^>]+>", "", h2).strip()
    my_head = head.replace(
        "<title>Чек-лист настройки Fitbase</title>",
        "<title>%s — Чек-лист Fitbase</title>" % html.escape(name),
    )
    page = (TEMPLATE
            .replace("__HEAD__", my_head)
            .replace("__BARSUB__", "Блок %s — %s" % (num, name))
            .replace("__MININUM__", "Блок %s" % num)
            .replace("__SECTION__", section)
            .replace("__JS__", STANDALONE_JS.replace("__STORE__", "fitbase_setup_%s" % bid)))
    outdir = os.path.join(HERE, bid)
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(page)
    print("  /setup/%s/  ->  %s" % (bid, name))

print("Готово.")
