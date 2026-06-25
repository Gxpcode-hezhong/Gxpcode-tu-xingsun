# GxpCode Skill — ④ 合并 LLM 分析结果到 S4
# 用法: python step4_merge.py gxpcode_data analysis.json
# analysis.json 格式: [{"source":"...","title":"...","summary":"...","tags":[...],"applicability":"high|medium|low|none","reason":"...","needs_manual_review":bool}, ...]

import json
import os
from collections import defaultdict

REQUIRED_FIELDS = ["summary", "tags", "applicability", "reason", "needs_manual_review"]


def _validate(entry: dict, index: int) -> list:
    """校验单条分析结果，返回缺失字段列表"""
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if "applicability" in entry and entry["applicability"] not in ("high", "medium", "low", "none"):
        missing.append(f"applicability={entry['applicability']} (invalid)")
    if missing:
        print(f"  [WARN] entry {index}: missing/invalid {missing}")
    return missing


def run(gxpcode: str, analysis_path: str):
    with open(analysis_path, "r", encoding="utf-8") as f:
        analyses = json.load(f)

    if not isinstance(analyses, list):
        print("ERROR: analysis.json must be a JSON array")
        return

    # 校验
    errors = sum(1 for i, a in enumerate(analyses) if _validate(a, i))
    if errors:
        print(f"  {errors} entries have validation issues, continuing anyway")

    # 按 source 分组写入 S4
    s4_dir = os.path.join(gxpcode, "s4")
    os.makedirs(s4_dir, exist_ok=True)
    for fname in os.listdir(s4_dir):
        if fname.endswith(".json"):
            os.remove(os.path.join(s4_dir, fname))

    src_groups = defaultdict(list)
    for entry in analyses:
        src_groups[entry.get("source", "unknown")].append(entry)

    for src, grp in src_groups.items():
        fname = f"s4_{src.replace('/', '_')}.json"
        path = os.path.join(s4_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(grp, f, ensure_ascii=False, indent=2)
        print(f"  {fname}: {len(grp)} items")

    # 写 .done
    with open(os.path.join(s4_dir, ".done"), "w") as f:
        f.write("")

    high = sum(1 for d in analyses if d.get("applicability") == "high")
    total = len(analyses)
    print(f"s4/: {total} items (high={high})")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python step4_merge.py gxpcode_data analysis.json")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
