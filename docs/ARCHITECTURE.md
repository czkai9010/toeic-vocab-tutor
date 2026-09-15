# 運作原理

## 全景

```
                    ┌──────────────────────────┐
   入口 A           │                          │
   Claude 對話框 ──►│   toeic-vocab-tutor      │
   「comply」       │   Skill                  │
                    │   (決定格式與口吻)       │
                    └───────────┬──────────────┘
                                │ write_db
                                ▼
                    ┌──────────────────────────┐
   入口 B           │   單字發音板 Artifact     │
   輸入框打字 ─────►│   ├─ db      單字庫       │◄──── 手機 / 平板 / 電腦
   「feasible」     │   └─ sample  問 Claude    │      看到的是同一份
                    └───────────┬──────────────┘
                                │ read_db
                                ▼
                    ┌──────────────────────────┐
                    │   build_vocab.py         │
                    │   JSON → MD + PDF        │
                    └───────────┬──────────────┘
                                │ 每日排程
                                ▼
                      本機資料夾 / iCloud
                      └─ 2026-01-06/ ...md .pdf
                      └─ _全部單字.md .pdf
```

兩個入口寫進**同一個** `db`,所以不管從哪裡加字,結果都一致。

---

## 資料格式

單字庫是一個 collection,路徑 `words`,每個字一份文件,文件 ID 是單字的 slug(小寫、非英數換成 `-`,例如 `in lieu of` → `in-lieu-of`)。

```json
{
  "word": "comply",
  "zh": "遵守、照辦(+ with)",
  "day": "2026-01-06",
  "createdAt": 1767657600000,
  "pos": ["v. 遵守、照辦(規定、要求、命令)"],
  "root": "com-(完全)+ ply(填滿),跟 complete 同源 —— 把對方要求的都填滿,就是「照辦」。",
  "coll": [
    "comply with the regulations — 遵守規定",
    "in compliance with — 依照、符合(名詞形,公告常見)",
    "failure to comply — 未能遵守(罰則條款愛用)"
  ],
  "ex": [
    { "en": "All employees must comply with the new safety guidelines.",
      "zh": "全體員工都必須遵守新的安全守則。" }
  ],
  "tip": "介系詞永遠是 with;公告合約看到名詞形 in compliance with,直接讀成「依照」。"
}
```

| 欄位 | 型別 | 說明 |
|---|---|---|
| `word` | string | 原拼寫,顯示與發音都用它 |
| `zh` | string | 一行中文,列表上顯示在單字下方 |
| `day` | string | `YYYY-MM-DD`,決定它歸在哪個日期分頁 |
| `createdAt` | number | epoch 毫秒,決定排序(新的在前) |
| `pos` `root` `coll` `ex` `tip` | — | 解析內容,點開單字時顯示;缺了也不會壞,只是那一段不顯示 |

只有 `word` 是必要的。**沒有解析的字照樣能存、能發音**,點開會出現「生成解析」按鈕。

---

## 三種能力

發音板宣告了兩個 capability,加上一個瀏覽器原生 API:

### `db` —— 雲端單字庫

Claude 平台提供的文件資料庫,綁在這個 Artifact 上。頁面用 `onSnapshot` 訂閱,任何裝置寫入,其他裝置立刻看到。

這是**跨裝置同步的全部祕密**:資料不在你電腦裡,所以不需要同步機制。

```js
const db = await claude.use("db");
db.collection("words").orderBy("createdAt", "desc").onSnapshot(render);
```

Claude 這端則用 `write_db` / `read_db` 讀寫同一個資料庫,所以對話框和頁面看到的永遠一致。

### `sample` —— 頁面自己問 Claude

讓網頁把問題送給 Claude 並拿回結構化答案。發音板用它在你打完字之後生成解析:

```js
const sample = await claude.use("sample");
const r = await sample.json(prompt(word), { modelTier: "default" });
// r = { zh, pos, root, coll, ex, tip }
```

要點:

- 第一次呼叫會**問使用者要不要授權**,拒絕就不生成。
- 費用算在**看頁面的人**的額度裡。
- 沒有記憶,每次都要把完整指示送進去 —— 所以 prompt 裡重複了 Skill 的格式要求。
- 會失敗(`rate_limited`、`not_granted`…),頁面對每種錯誤都有對應訊息,單字本身一定先存下來。

### `speechSynthesis` —— 發音

瀏覽器原生 API,不需要任何 capability、任何 API key、任何網路請求。語音清單來自使用者的作業系統,所以 macOS / iOS 的品質最好。

一個實作上的坑:**iOS 不允許用 `onend` 串接連續語音**。所以「依序播放」是在同一次點擊裡把整批 utterance 一次排進佇列,而不是播完一個再排下一個。

---

## 備份產生器

`scripts/build_vocab.py` 是純 Python,沒有第三方相依。

```
python3 build_vocab.py <docs_dir> <out_dir>
```

- `<docs_dir>` —— `read_db` 用 `out_dir` 匯出的資料夾(一堆 `<單字>.json`)。腳本能容忍 `{id, data, version}` 包裝格式。
- `<out_dir>` —— 產出位置。

流程:讀 JSON → 按 `day` 分組 → 每天產一份 MD 與 HTML → HTML 用 headless Chromium 印成 PDF → 再產一份字母序的總匯整。

PDF 的部分:

- 找 Chromium 的順序寫在 `CHROME_CANDIDATES`,找不到就只產 MD 並印一行警告,不會整個失敗。
- 中文需要 **Noto Sans CJK**;缺字型會變方框。
- 版面刻意壓緊到一頁約兩個字,34 個字大約 17 頁。

---

## 為什麼是這個架構

| 決定 | 原因 |
|---|---|
| 單字庫放 Artifact 的 `db`,不放檔案 | 檔案要同步,資料庫不用。手機平板開同一個網址就是同一份。 |
| 解析存進 `db`,不只存在對話紀錄 | 對話會被翻過去,資料庫不會。點單字就能調出來。 |
| 發音用瀏覽器原生 API,不用 TTS 服務 | 零成本、零延遲、離線可用,而且 iOS 的內建語音比多數雲端 TTS 自然。 |
| 備份同時產 MD 與 PDF | MD 給 Notion / Obsidian 這種吃純文字的;PDF 給 Notability 這種要手寫註記的。Notability 不會渲染 Markdown。 |
| 一天一個資料夾 | 對應「每天一批題目」的節奏,複習時直接找日期。 |
| Skill 和頁面各有一份 prompt | 兩個入口要能獨立運作。改格式時兩邊都要改 —— 這是這個設計唯一的維護成本。 |
