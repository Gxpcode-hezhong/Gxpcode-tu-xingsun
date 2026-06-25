# GxpCode Skill — S1 web 源拉取

import json
import os
import re
import time
import yaml
from playwright.sync_api import sync_playwright
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def _parse_body(body: str, extract: dict) -> list:
    """解析 innerText，按 extract 规则提取 title + date"""
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    date_mode = extract.get("date_pattern", "")

    entries = []
    if date_mode == "行模式":
        i = 0
        while i < len(lines):
            # CDE: 2026.06 01  或  NMPA-fgwj: (2026-06-01)
            m = re.match(r"^(?:\d{4}\.\d{2} \d{2}|\(\d{4}-\d{2}-\d{2}\))$", lines[i])
            if m and i + 1 < len(lines) and "共" not in lines[i + 1]:
                entries.append({
                    "date": lines[i].strip("()").replace(" ", "-"),
                    "title": lines[i + 1].replace(">", "").strip(),
                })
                i += 2
            else:
                i += 1
    elif date_mode == "括号内":
        for line in lines:
            m = re.search(r"(.+) \((\d{4}-\d{2}-\d{2})\)$", line)
            if m:
                entries.append({"title": m.group(1), "date": m.group(2)})
    else:
        for line in lines:
            if len(line) >= 15:
                entries.append({"title": line, "date": ""})

    return entries



def _parse_data_order(page) -> list:
    """data-order 模式：日期在 td 的 data-order 属性里"""
    entries = []
    for td in page.query_selector_all("td[data-order]"):
        do = td.get_attribute("data-order") or ""
        m = re.match(r"(\d{4}-\d{2}-\d{2})", do)
        if not m:
            continue
        date = m.group(1)
        a = td.query_selector("a[href]")
        if not a:
            continue
        title = a.inner_text().strip()
        url = a.evaluate("el => el.href")
        if not title or not url:
            continue
        entries.append({"title": title, "url": url, "date": date})
    return entries


def _pair_links(entries: list, page, extract: dict) -> list:
    """把标题和链接配对"""
    link_by = extract.get("link_by", "title")

    if link_by == "title":
        all_links = {}
        for a in page.query_selector_all("a[href]"):
            text = a.inner_text().strip()
            url = a.evaluate("el => el.href")
            if len(text) >= 10 and url:
                all_links[text] = url
        for e in entries:
            t = e["title"]
            if t in all_links:
                e["url"] = all_links[t]
            else:
                best = ""
                for k, v in all_links.items():
                    if len(k) >= 15 and (k[:20] in t or t[:20] in k):
                        best = v
                        break
                e["url"] = best
    else:
        text_match = link_by.replace("text:", "")
        link_list = []
        for a in page.query_selector_all("a"):
            if a.inner_text().strip() == text_match:
                link_list.append(a.evaluate("el => el.href"))
        for i, e in enumerate(entries):
            e["url"] = link_list[i] if i < len(link_list) else ""

    return entries


def run(sources_path: str, gxpcode: str):
    s1_dir = os.path.join(gxpcode, "s1")
    os.makedirs(s1_dir, exist_ok=True)

    with open(sources_path, "r", encoding="utf-8") as f:
        sources = yaml.safe_load(f).get("sources", [])

    web_sources = [s for s in sources if s.get("type") == "web"]
    if not web_sources:
        print("No web sources found")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )

        for src in web_sources:
            name = src["name"]
            url = src["url"]
            jurisdiction = src.get("jurisdiction", "")
            extract = src.get("extract", {})

            print(f"[{name}] {url[:60]}...")
            page = context.new_page()
            try:
                page.goto(url, timeout=30000, wait_until="networkidle")
                time.sleep(3)

                date_mode = extract.get("date_pattern", "")
                if date_mode == "data-order":
                    entries = _parse_data_order(page)
                else:
                    body = page.evaluate("() => document.body.innerText")
                    entries = _parse_body(body, extract)
                    entries = _pair_links(entries, page, extract)

                items = []
                for e in entries:
                    title = e.get("title", "")
                    url_item = e.get("url", "")
                    if not title or not url_item:
                        continue
                    items.append({
                        "source": name,
                        "jurisdiction": jurisdiction,
                        "title": title,
                        "url": url_item,
                        "date": e.get("date", ""),
                        "summary": "",
                        "source_type": "web",
                        "confidence": "high",
                    })

                path = os.path.join(s1_dir, f"s1_{name.replace('/', '_')}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(items, f, ensure_ascii=False, indent=2)
                print(f"  → {len(items)} items → {path}")
            except Exception as e:
                print(f"  FAIL: {e}")
            finally:
                page.close()

        browser.close()


if __name__ == "__main__":
    import sys
    run(sys.argv[1], sys.argv[2])
