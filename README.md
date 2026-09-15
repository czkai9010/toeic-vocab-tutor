# TOEIC 單字家教 · Vocab Tutor

**主題:一套用 Claude 打造的多益單字學習系統 —— 貼上生字,拿到家教等級的解析,存進會發音的雲端單字庫,每天自動備份成 MD 與 PDF。**

> A self-hosted TOEIC vocabulary tutor built on Claude Cowork:
> paste a word → get a tutor-style breakdown → it lands in a speaking,
> date-organised word bank that backs itself up to Markdown and PDF every night.

---

## 摘要

寫多益題本最花時間的不是做題,是**遇到生字之後的處理**:查意思、抄筆記、隔天忘光、想複習時找不到當初抄在哪。

這套系統把那段流程整個接起來,一共四個零件:

| 零件 | 做什麼 |
|---|---|
| **單字家教 Skill** | 你貼一個英文單字,Claude 用固定格式回你:詞性與意思、字根拆解、常見搭配、3 句多益語境例句、一句提點。口吻是家教,不是字典。 |
| **單字發音板 Artifact** | 一個雲端網頁。單字用瀏覽器內建語音唸出來(可調語速、切英美腔),按學習日期分類,點單字就展開完整解析。手機、平板、電腦同一份資料即時同步。 |
| **備份產生器** | 把整個單字庫輸出成 Markdown 與 PDF,一天一個資料夾加一份總匯整。MD 進 Notion / Obsidian,PDF 丟 Notability 手寫劃重點。 |
| **每日排程** | 每天固定時間自動跑一次備份,寫進你指定的本機資料夾與 iCloud。 |

兩個入口,結果一樣:

- **在 Claude 對話框貼單字** → Skill 回你完整解析,同時把字寫進發音板。
- **在發音板的輸入框打單字** → 頁面自己向 Claude 要解析,幾秒後填好。不必開對話框。

---

## 它長什麼樣

單字卡的固定格式(以 `comply` 為例):

```
詞性與意思   v. 遵守、照辦(規定、要求、命令)
字根拆解     com-(完全)+ ply(填滿),跟 complete 同源 —— 把對方要求的都填滿,就是「照辦」。
常見搭配     comply with the regulations — 遵守規定
             in compliance with — 依照、符合(名詞形,公告常見)
             failure to comply — 未能遵守(罰則條款愛用)
例句         All employees must comply with the new safety guidelines.
             全體員工都必須遵守新的安全守則。
             (共 3 句,涵蓋不同用法)
提點         介系詞永遠是 with;公告合約看到名詞形 in compliance with,直接讀成「依照」。
```

---

## 快速開始

需要 [Claude](https://claude.ai) 帳號(Cowork 模式)。**完整步驟看 [docs/SETUP.md](docs/SETUP.md)**,最短路徑是:

1. 把 `skill/toeic-vocab-tutor/SKILL.md` 存成你的 Skill。
2. 請 Claude 用 `artifact/pronounce.html` 發布一個 Artifact(需要 `db` 與 `sample` 兩個 capability)。
3. 把拿到的網址填回 Skill 裡的 `PASTE_YOUR_ARTIFACT_URL_HERE`。
4. 開始貼單字。

想先看看資料長什麼樣,`data/sample/words/` 裡有 5 個字的完整範例。

---

## 目錄

```
skill/toeic-vocab-tutor/SKILL.md   單字家教 Skill(核心;決定解析的格式與口吻)
artifact/pronounce.html            發音板網頁原始碼(單一檔案,無外部相依)
scripts/build_vocab.py             備份產生器:單字庫 JSON → MD + PDF
automation/daily-backup-task.md    每日自動備份排程的設定與 prompt
data/sample/words/                 5 個字的範例資料,可直接匯入試跑
docs/SETUP.md                      教學手冊:從零到能用
docs/ARCHITECTURE.md               運作原理與資料格式
docs/CUSTOMIZE.md                  改成你自己的考試、語言、格式
```

---

## 設計上的幾個決定

這些是踩過才知道的,寫下來給想改的人參考:

- **字根拆解要誠實。** `itinerary`、`agenda` 這種字沒有好拆的字根,硬拆會編出假字源害人記錯。Skill 明文要求這種情況改給記憶鉤子,並直說沒有字根可拆。
- **例句三句必須真的不同。** 不然很容易變成同一個句型換三個主詞,等於只有一句。
- **介系詞搭配優先。** `comply **with**`、`specialist **in**`、`allocate **to**` —— 那正是多益 Part 5 最愛考的點。
- **備份同時給 MD 和 PDF。** Notability 不會渲染 Markdown,直接匯 MD 進去會看到一堆 `**` 符號;PDF 才能直接手寫註記。兩種格式對應兩種用途。
- **單字庫放雲端,不放本機。** 這樣手機、平板、電腦看到的是同一份;本機資料夾只放輸出的檔案。

---

## 授權

MIT。拿去改、拿去用都可以。

如果你把它改成別的考試或語言(IELTS、日檢、GRE…),歡迎開 issue 說一聲,我很想知道。
