#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多益單字備份產生器。

用法:  python3 build_vocab.py <docs_dir> <out_dir>

<docs_dir>  Artifact read_db 用 out_dir 匯出的資料夾(裡面是一堆 <單字>.json)
<out_dir>   產出位置。結構:
              <out_dir>/YYYY-MM-DD/YYYY-MM-DD.md
              <out_dir>/YYYY-MM-DD/YYYY-MM-DD.pdf
              <out_dir>/_全部單字.md
              <out_dir>/_全部單字.pdf
每個單字的 JSON 欄位:word, zh, day, createdAt, pos[], root, coll[], ex[{en,zh}], tip
"""
import json, os, sys, glob, html, datetime, subprocess, hashlib

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
]

CSS = """
@page { size: A4; margin: 14mm 14mm 12mm; }
* { box-sizing: border-box; }
body { margin:0; color:#16202B;
  font-family:"Noto Sans CJK TC","Noto Sans TC",-apple-system,sans-serif;
  font-size:9.3pt; line-height:1.5; }
h1 { font-size:17pt; margin:0 0 3px; letter-spacing:-.01em; }
.sub { color:#66727E; font-size:8.5pt; margin:0 0 3px; }
.rule { border-bottom:1.2pt solid #16202B; margin:7px 0 13px; }
.entry { break-inside:avoid; page-break-inside:avoid; margin-bottom:12px;
  padding-bottom:10px; border-bottom:.5pt solid #D6DDE3; }
.entry:last-child { border-bottom:0; }
.hw { font-family:"DejaVu Sans Mono",monospace; font-size:12pt; font-weight:700;
  color:#0B5B6B; margin:0 0 5px; }
.hw .n { color:#9AA6B1; font-size:8.5pt; font-weight:400; margin-right:7px; }
.lbl { font-size:7.2pt; font-weight:700; letter-spacing:.1em; color:#0B5B6B;
  margin:6px 0 2px; text-transform:uppercase; }
ul { margin:0; padding-left:16px; }
li { margin:1px 0; }
p.body { margin:0; }
ol.ex { margin:0; padding-left:16px; }
ol.ex li { margin:0 0 3px; }
ol.ex .en { font-family:"DejaVu Serif",Georgia,serif; }
ol.ex .zh { color:#4B5A67; display:block; }
.tip { background:#F1F5F7; border-left:2.5pt solid #0B5B6B;
  padding:4px 8px; margin:0; color:#28333E; }
"""

WD = "一二三四五六日"


def zh_date(iso):
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        return "%d 年 %d 月 %d 日(星期%s)" % (y, m, d, WD[datetime.date(y, m, d).weekday()])
    except Exception:
        return iso


def load(docs_dir):
    out = []
    for p in glob.glob(os.path.join(docs_dir, "**", "*.json"), recursive=True):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        if isinstance(d, dict) and "data" in d and isinstance(d["data"], dict):
            d = d["data"]                      # tolerate {id,data,version} wrappers
        if not isinstance(d, dict) or not d.get("word"):
            continue
        d.setdefault("zh", "");   d.setdefault("day", "未分類")
        d.setdefault("pos", []);  d.setdefault("root", "")
        d.setdefault("coll", []); d.setdefault("ex", []); d.setdefault("tip", "")
        d.setdefault("createdAt", 0)
        out.append(d)
    return out


def esc(s):
    return html.escape(str(s), quote=False)


# ---------------- Markdown ----------------
def md_entry(w, n):
    L = ["## %d. %s" % (n, w["word"]), ""]
    if w["zh"]:
        L += ["`%s`" % w["zh"], ""]
    if w["pos"]:
        L += ["**詞性與意思**", ""] + ["- " + s for s in w["pos"]] + [""]
    if w["root"]:
        L += ["**字根拆解**", "", w["root"], ""]
    if w["coll"]:
        L += ["**常見搭配**", ""] + ["- " + s for s in w["coll"]] + [""]
    if w["ex"]:
        L += ["**例句**", ""]
        for i, e in enumerate(w["ex"], 1):
            L += ["%d. %s" % (i, e.get("en", "")), "   %s" % e.get("zh", "")]
        L += [""]
    if w["tip"]:
        L += ["**提點**", "", w["tip"], ""]
    L += ["---", ""]
    return "\n".join(L)


def md_doc(title, subtitle, ws):
    L = ["# " + title, "", "> " + subtitle, "", "---", ""]
    L += [md_entry(w, i) for i, w in enumerate(ws, 1)]
    return "\n".join(L).rstrip() + "\n"


# ---------------- HTML / PDF ----------------
def html_entry(w, n):
    P = ["<div class='entry'>",
         "<p class='hw'><span class='n'>%02d</span>%s</p>" % (n, esc(w["word"]))]
    if w["pos"]:
        P += ["<p class='lbl'>詞性與意思</p><ul>"] + ["<li>%s</li>" % esc(s) for s in w["pos"]] + ["</ul>"]
    elif w["zh"]:
        P += ["<p class='lbl'>意思</p><p class='body'>%s</p>" % esc(w["zh"])]
    if w["root"]:
        P += ["<p class='lbl'>字根拆解</p><p class='body'>%s</p>" % esc(w["root"])]
    if w["coll"]:
        P += ["<p class='lbl'>常見搭配</p><ul>"] + ["<li>%s</li>" % esc(s) for s in w["coll"]] + ["</ul>"]
    if w["ex"]:
        P += ["<p class='lbl'>例句</p><ol class='ex'>"]
        for e in w["ex"]:
            P.append("<li><span class='en'>%s</span><span class='zh'>%s</span></li>"
                     % (esc(e.get("en", "")), esc(e.get("zh", ""))))
        P.append("</ol>")
    if w["tip"]:
        P += ["<p class='lbl'>提點</p><p class='tip'>%s</p>" % esc(w["tip"])]
    P.append("</div>")
    return "\n".join(P)


def html_doc(title, subtitle, ws):
    body = "\n".join(html_entry(w, i) for i, w in enumerate(ws, 1))
    return ("<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'>"
            "<title>%s</title><style>%s</style></head><body>"
            "<h1>%s</h1><p class='sub'>%s</p><div class='rule'></div>%s"
            "</body></html>" % (esc(title), CSS, esc(title), esc(subtitle), body))


def chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    return None


def to_pdf(html_path, pdf_path):
    c = chrome()
    if not c:
        print("  ! 找不到 chromium,略過 PDF:" + os.path.basename(pdf_path))
        return False
    subprocess.run([c, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=8000",
                    "--print-to-pdf=" + os.path.abspath(pdf_path),
                    "file://" + os.path.abspath(html_path)],
                   check=True, capture_output=True, timeout=300)
    return True


def digest(ws):
    """一批單字的內容指紋。內容沒變就不用重印。"""
    payload = json.dumps(
        sorted(ws, key=lambda w: (w.get("createdAt", 0), w["word"])),
        ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def load_state(out_dir):
    p = os.path.join(out_dir, "_state.json")
    try:
        with open(p, encoding="utf-8") as f:
            s = json.load(f)
        return s if isinstance(s, dict) else {}
    except Exception:
        return {}


def save_state(out_dir, state):
    with open(os.path.join(out_dir, "_state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)


def emit(out_dir, stem, title, sub, ws, made):
    os.makedirs(os.path.dirname(os.path.join(out_dir, stem)) or out_dir, exist_ok=True)
    base = os.path.join(out_dir, stem)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write(md_doc(title, sub, ws))
    made.append(base + ".md")
    hp = base + ".__tmp.html"
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html_doc(title, sub, ws))
    ok = to_pdf(hp, base + ".pdf")
    os.remove(hp)
    if ok:
        made.append(base + ".pdf")


MASTER_PDF_LIMIT = 600   # 總匯整超過這個字數就不再印 PDF(MD 仍然每次更新)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    docs_dir, out_dir = args[0], args[1]
    words = load(docs_dir)
    if not words:
        print("沒有讀到任何單字,結束。")
        sys.exit(2)
    os.makedirs(out_dir, exist_ok=True)

    state = {} if force else load_state(out_dir)
    old_days = state.get("days", {}) if isinstance(state.get("days"), dict) else {}
    new_days, made, skipped = {}, [], 0

    days = {}
    for w in words:
        days.setdefault(w["day"], []).append(w)

    for day, ws in sorted(days.items()):
        ws.sort(key=lambda x: x.get("createdAt", 0))          # 當天照學習順序
        h = new_days[day] = digest(ws)
        md = os.path.join(out_dir, day, day + ".md")
        if old_days.get(day) == h and os.path.exists(md):
            skipped += 1
            continue
        emit(out_dir, os.path.join(day, day),
             "多益單字 · " + zh_date(day),
             "共 %d 個字 · 學習日 %s" % (len(ws), day), ws, made)

    # 總匯整:MD 每次都更新(便宜),PDF 只在有變動且字數不過大時重印
    allw = sorted(words, key=lambda w: w["word"].lower())
    master_h = digest(allw)
    title = "多益單字總匯整"
    sub = "共 %d 個字 · 依字母排序 · 更新於 %s" % (len(allw), datetime.date.today().isoformat())
    mbase = os.path.join(out_dir, "_全部單字")
    with open(mbase + ".md", "w", encoding="utf-8") as f:
        f.write(md_doc(title, sub, allw))
    made.append(mbase + ".md")
    if state.get("master") != master_h:
        if len(allw) <= MASTER_PDF_LIMIT:
            hp = mbase + ".__tmp.html"
            with open(hp, "w", encoding="utf-8") as f:
                f.write(html_doc(title, sub, allw))
            if to_pdf(hp, mbase + ".pdf"):
                made.append(mbase + ".pdf")
            os.remove(hp)
        else:
            print("  · 總匯整已達 %d 字(上限 %d),只更新 MD,不再重印 PDF。"
                  "每日 PDF 仍然照常產出。" % (len(allw), MASTER_PDF_LIMIT))

    save_state(out_dir, {"days": new_days, "master": master_h,
                         "updatedAt": datetime.datetime.now().isoformat(timespec="seconds")})

    print("完成:%d 天、%d 個字(重建 %d 天,略過 %d 天未變動)"
          % (len(days), len(words), len(days) - skipped, skipped))
    if not made:
        print("沒有任何檔案需要更新。")
    for p in made:
        print("%9d  %s" % (os.path.getsize(p), p))


if __name__ == "__main__":
    main()
