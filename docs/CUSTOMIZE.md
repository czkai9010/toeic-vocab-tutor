# 客製化

這套東西是為了「繁體中文母語者準備多益」做的。想改成別的用途,下面是每個改動要動哪幾個檔案。

> **通則:單字卡的格式定義在兩個地方** —— Skill(`skill/toeic-vocab-tutor/SKILL.md`)與發音板裡的 `prompt()` 函式(`artifact/pronounce.html`)。兩個入口要獨立運作,所以格式改動**兩邊都要改**,否則你會發現從對話框加的字和從頁面加的字長得不一樣。

---

## 換成別的考試

多益的痕跡集中在三個地方:

1. **Skill 的〈撰寫原則〉** —— 「例句貼近多益語感。多益的世界是辦公室、公告、合約、出差、客訴、會議。」
2. **Skill 的〈家教提點〉欄位說明** —— 提到 Part 5、Part 7。
3. **發音板 `prompt()` 裡的同兩句。**

改成雅思:

```
- 例句語境貼近雅思:學術討論、圖表描述、社會議題、校園生活。
- tip 只寫一到兩句,講這個字在 Writing Task 2 或 Speaking 怎麼用得上。
```

改成 GRE:

```
- 例句語境貼近 GRE:學術論述、實驗描述、書評。
- tip 只寫一到兩句,講這個字最常見的難義,以及容易被拿來當干擾選項的近義字。
```

---

## 換成別的母語

把兩份 prompt 裡的「繁體中文」換成目標語言,並把 `zh` 欄位理解成「母語解釋」即可 —— 欄位名稱不用改,改了反而要同步改頁面與腳本。

介面文字在 `artifact/pronounce.html` 的 HTML 區塊,直接改字串。`WD = "一二三四五六日"` 是星期的顯示,也在腳本裡有一份。

---

## 改單字卡的欄位

假設你想加一個「易混淆字」欄位:

1. **Skill**:在卡片格式與撰寫原則裡加上這一欄。
2. **`prompt()`**:在回傳的 JSON 結構裡加 `"confuse": ["similar word — 差在哪"]`。
3. **`openDetail()`**:加一行

   ```js
   if (w.confuse && w.confuse.length) sheetBody.appendChild(sec("易混淆", ulOf(w.confuse)));
   ```
4. **db 對映**(`onSnapshot` 那段):加 `confuse: Array.isArray(v.confuse) ? v.confuse : []`。
5. **`build_vocab.py`**:在 `md_entry()` 與 `html_entry()` 各加一段,並在 `load()` 的 `setdefault` 補上預設值。

反過來要拿掉某一欄,把上面五處對應的部分刪掉就好;舊資料留著多餘欄位不會出問題。

---

## 改發音

| 想改什麼 | 改哪裡 |
|---|---|
| 預設語速 | `artifact/pronounce.html` 的 `state.rate`(預設 `0.9`)與 `<input id="rate" value="0.9">` |
| 慢速的速度 | 搜尋 `rate:0.55` |
| 預設英美腔 | `state.lang`(`"en-US"` / `"en-GB"`) |
| 偏好的語音 | `loadVoices()` 裡的 `nice` 陣列,依序比對名稱開頭 |
| 換掉 ICAO 拼讀 | `ICAO` 常數;想關掉就移除「拼讀」按鈕 |

---

## 改 PDF 版面

全部在 `scripts/build_vocab.py` 的 `CSS` 常數裡,是一般的 CSS。

| 想改什麼 | 改哪裡 |
|---|---|
| 一頁放幾個字 | `body { font-size }` 與 `.entry { margin-bottom / padding-bottom }`。字級調小就塞得多。 |
| 允許一個字跨頁 | 移除 `.entry` 的 `break-inside: avoid`。適合字數多、不介意跨頁的人。 |
| 紙張大小 | `@page { size: A4 }` → `letter`、`A5` 等 |
| 配色 | `.hw`、`.lbl` 的 `color`(主色 `#0B5B6B`) |
| 中文字型 | `body { font-family }`。產生 PDF 的環境要真的有那套字型。 |

---

## 改備份的檔案結構

`build_vocab.py` 的 `main()` 底部:

```python
emit(out_dir, os.path.join(day, day), ...)   # → 2026-01-06/2026-01-06.md
```

改成一天一個檔、不開資料夾:

```python
emit(out_dir, day, ...)                      # → 2026-01-06.md
```

一個字一個檔(適合 Obsidian 雙向連結):

```python
for w in words:
    emit(out_dir, os.path.join("words", w["word"]),
         w["word"], w.get("zh", ""), [w], made)
```

---

## 換成別的備份目的地

備份檔怎麼落地是**排程任務的 prompt** 在管,不是腳本。打開 `automation/daily-backup-task.md`,改裡面的路徑清單。

- **只要雲端不要本機**:把 `device_commit_files` 那段換成上傳到 Google Drive 或 Notion 的連接器。
- **要 Git 版控**:讓排程 commit 進一個 repo,這樣每天的單字都有歷史紀錄。
- **要寄到信箱**:改成用 Gmail 連接器把 PDF 當附件寄給自己。

---

## 不想用排程

備份完全可以手動跑,任何時候對 Claude 說一句「幫我備份單字」就好。排程只是省下這句話。

想完全不要備份,只用雲端單字庫,那就跳過 `scripts/` 和 `automation/` —— Skill 與 Artifact 兩個零件本身是完整的。
