# 範例資料

5 個字的完整範例,格式跟真實單字庫一模一樣,可以拿來:

- 看清楚每個欄位長什麼樣(格式說明在 [../../docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md))
- 不用先累積單字就試跑備份產生器:

```bash
python3 scripts/build_vocab.py data/sample/words /tmp/out
```

跑完 `/tmp/out/` 底下會出現 `2026-01-06/2026-01-06.md`、`.pdf` 與 `_全部單字.md`、`.pdf`。

日期一律標成 `2026-01-06`,純粹是為了讓範例落在同一個日期資料夾裡。
