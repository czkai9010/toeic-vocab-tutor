# 每日自動備份

讓 Claude 每天固定時間把整個單字庫輸出成 MD 與 PDF,寫進你的資料夾。

---

## 事前準備

1. **連結資料夾。** 在 Claude 桌面 app 裡連結你要當備份位置的資料夾。想讓 iPad 讀得到,連結一個 iCloud 雲端硬碟底下的資料夾。
2. **放好腳本。** 把 `scripts/build_vocab.py` 放進備份資料夾的 `_tools/` 子資料夾。排程每次執行時會從那裡取用,所以它必須留在那。
3. **手動跑一次確認沒問題**,再設排程。

---

## 建立排程

對 Claude 說「幫我建立一個每天 X 點執行的排程任務」,並把下面的 prompt 給它。

**執行前先替換三處:**

| 佔位符 | 換成 |
|---|---|
| `<ARTIFACT_URL>` | 你的發音板網址 |
| `<BACKUP_DIR>` | 本機備份資料夾的絕對路徑 |
| `<CLOUD_DIR>` | iCloud / 雲端資料夾的絕對路徑(不需要就把第 4 步的第二個路徑刪掉) |

---

## 排程 prompt

```
每天自動備份我的單字庫。全部用繁體中文,做完簡短回報即可,不要長篇大論。

步驟:

1. 用 Artifact 工具把單字庫匯出成 JSON:
   action="read_db"
   url="<ARTIFACT_URL>"
   db_op="list", collection="words", query={"limit":1000}
   out_dir="/home/claude/dump"
   若結果帶 next_cursor,用 query.cursor 續讀直到全部讀完。

2. 把產生器腳本從我的電腦抓進容器:
   mcp__remote-devices__device_stage_files
   paths=["<BACKUP_DIR>/_tools/build_vocab.py"]
   把回傳的 stagedPath 複製到 /home/claude/build_vocab.py

3. 執行產生器(它會自己找 chromium 產 PDF):
   python3 /home/claude/build_vocab.py /home/claude/dump /home/claude/built
   產出結構:built/<YYYY-MM-DD>/<YYYY-MM-DD>.md 與 .pdf,以及 built/_全部單字.md 與 .pdf

4. 把 built 底下每個檔案複製到 /mnt/user-data/outputs/(檔名會撞名的話自己加前綴),
   再用 mcp__remote-devices__device_commit_files 搭配 force=true 寫回下面兩個位置,
   資料夾結構要跟 built 一模一樣(日期資料夾要保留):
   - <BACKUP_DIR>/
   - <CLOUD_DIR>/

5. 回報:備份了幾天、共幾個字、寫進哪些路徑。如果某天的字沒有詳細解析,順帶提一下是哪幾個字。

如果連不上我的電腦(多半是筆電睡著了),說明一次就結束,不要反覆重試。
```

---

## 挑時間

排程是用 UTC 記的,但你跟 Claude 講當地時間就好,它會換算。

**要注意的是你的電腦醒著沒有。** 排程跑的時候筆電闔上或睡著,那次就會跳過(隔天會補上,因為腳本每次都重建全部日期)。

| 時間 | 適合誰 |
|---|---|
| 晚上 10–11 點 | 大部分人。這時候通常還在用電腦。 |
| 半夜 12 點 | 你習慣熬夜,或電腦設定為不休眠。 |
| 早上 8 點 | 你早上開機比較準時。備份的是前一天的字。 |

---

## 驗證

隔天打開備份資料夾,應該看到:

```
<BACKUP_DIR>/
├── 2026-01-06/
│   ├── 2026-01-06.md
│   └── 2026-01-06.pdf
├── _全部單字.md
├── _全部單字.pdf
└── _tools/
    └── build_vocab.py
```

沒有跑起來的話,對 Claude 說「列出我的排程任務」看看它的最後執行狀態。

---

## 這個排程是冪等的

每次執行都會**重建全部日期的檔案**,不是只補當天。所以:

- 漏跑一天不會缺資料,隔天自動補齊。
- 你事後補的解析,下次備份就會反映進去。
- 手動多跑幾次不會有副作用。

代價是單字量很大之後每次都要重印全部 PDF。到幾千個字以後才需要考慮改成只重建有變動的日期。
