# Step 3 — 获取

```bash
python "${SKILL_DIR}/scripts/step3_fetch.py" gxpcode_data
```

输入: `gxpcode_data/s2/`（按域名并发，BATCH=5 刷新 context，空 body 最多重试 2 次）
输出: `gxpcode_data/s3/s3_{源名}.json` + `s3/.done` + `outputs/pdfs/`

s2/ 为空则跳过 S3。
