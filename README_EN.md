[English](README_EN.md) | [中文](README.md)
# Tu-Xingsun · GxpCode Regulatory Tracking Skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](scripts/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Scan · Compare · Analyze · Report** — A pharmaceutical regulatory compliance monitoring workflow

Automatically scans global regulatory sources — NMPA, CDE, FDA, EMA, ICH, PIC/S — discovers new regulations, guidelines, draft guidance, and notices; produces summaries, assigns tags and applicability judgments, and generates structured PDF reports.

> "土行孙" (Tǔ Xíng Sūn) — a figure from Chinese mythology who can travel a thousand miles underground in a single night. Our bot does the same for regulatory documents.

---

## Quick Start

```bash
# 1. Install dependencies & configure environment
python scripts/setup.py
```

The `setup.py` script handles venv creation, pip dependency installation, and Playwright browser setup automatically.

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-source Scanning** | 16 pre-configured regulatory sources across NMPA (10), CDE (2), CDR-ADR (1), FDA (1), EMA (1), PIC/S (1) |
| **5-route Architecture** | `playwright` / `rss` / `api` / `mcp` / `requests` — automatically selects the best adapter per source |
| **Intelligent Deduplication** | Joint key dedup — agency + title hash + URL fragment — with persistent history |
| **AI-powered Analysis** | LLM-driven summarization, multi-label tagging, applicability scoring (applicable / needs review / not applicable) |
| **Change Detection** | Classifies entries as: `new` / `revision` / `abolished` / `draft` |
| **Traffic-light Coding** | Red · Yellow · Green · Gray levels for urgency and applicability at a glance |
| **PDF Report Generation** | Structured PDF reports with index, source overview, item-level detail, and regulatory lifecycle visualization |
| **Fault-tolerant Execution** | 4-tier error matrix: `FATAL` / `SOURCE_SKIP` / `ITEM_SKIP` / `DEGRADED` |
| **Batch Control** | Max 20 items per batch to stay within LLM context limits |

---

## Workflow

```
┌───────────────────────────────────────────────────────────┐
│                         GxpCode Pipeline                   │
│                                                           │
│  Step 1           Step 2          Step 3        Step 4     │         Step 5
│  ┌───────┐       ┌───────┐       ┌───────┐     ┌───────┐  │        ┌───────┐
│  │Detect │──────▶│Compare│──────▶│ Fetch │────▶│Analyze│──▶        │Notify │
│  │& Fetch│       │& Diff │       │Content│     │& Tag  │  │        │&Report│
│  └───────┘       └───────┘       └───────┘     └───────┘  │        └───────┘
│      │               │               │             │      │            │
│      ▼               ▼               ▼             ▼      │            ▼
│  scrape list      new/changed     full text     structured │     PDF + msg
│  from sources     entries only    of each       analysis  │     delivered
│                                   entry         JSON      │
└───────────────────────────────────────────────────────────┘
        ▲ optional: Step A — manual single-item deep analysis
```

### Step Breakdown

| Step | Name | Description |
|------|------|-------------|
| **S1** | Detect | Scrape regulatory source pages, collect entry metadata (title, date, URL) |
| **S2** | Compare | Diff against history; identify new / changed / removed entries |
| **S3** | Fetch | Retrieve full text content for new/changed entries |
| **S4** | Analyze | LLM-driven: summarize, tag, assess applicability, assign traffic-light level |
| **S5** | Notify | Assemble and deliver PDF report + message notification |
| **SA** | Single Analyze | One-off deep analysis for an individual document |

---

## Monitoring Sources (16 total)

| # | Source | Agency | Type | Adapter |
|---|--------|--------|------|---------|
| 1 | NMPA — BGT | NMPA | Notices | web |
| 2 | NMPA — FGS (laws & regulations) | NMPA | Regulations | web |
| 3 | NMPA — YPS (drug product registration) | NMPA | Announcements | web |
| 4 | NMPA — YPS (review progress) | NMPA | Progress | web |
| 5 | NMPA — YPS (notification letters) | NMPA | Letters | web |
| 6 | NMPA — ZLS (quality management) | NMPA | GMP/GSP | web |
| 7 | NMPA — OCT | NMPA | OTC | web |
| 8 | NMPA — CSO | NMPA | Cosmetics | web |
| 9 | NMPA — YPSRZL | NMPA | Certification | web |
| 10 | NMPA — FGS (policy interpretation) | NMPA | Policy briefs | web |
| 11 | CDE — News | CDE | News | playwright |
| 12 | CDE — Notices & Announcements | CDE | Notices | playwright |
| 13 | CDR-ADR — Notifications | CDR-ADR | Safety alerts | web |
| 14 | FDA — What's New (Drugs) | FDA | News/Guidance | rss |
| 15 | EMA — What's New | EMA | News/Guidance | rss |
| 16 | PIC/S — Publications | PIC/S | Guidelines | api |

> **Note:** CDE pages load content via JavaScript (JS-rendered async components). The `playwright` adapter is used for these sources to ensure PDF attachments are properly triggered for download.

---

## Directory Structure

```
GxpCode-tu-xingsun/
├── README.md                  # This file
├── CHANGELOG.md               # Version history
├── SKILL.md                   # Competencies & instruction set
├── LICENSE                    # MIT License
├── scripts/
│   ├── setup.py               # One-click environment setup
│   ├── requirements.txt       # Python dependencies
│   ├── step1_web.py           # Web scraper (NMPA / FDA / EMA / PIC/S)
│   ├── step1_rss.py           # RSS feed parser (FDA / EMA)
│   ├── step2_compare.py       # History diff — new/changed/removed
│   ├── step3_fetch.py         # Full-content fetcher
│   ├── step4_merge.py         # Batch assembly & merge
│   ├── step5_notify.py        # PDF report + notification dispatch
│   ├── stepA_analyze.py       # Single-item deep analysis (manual)
│   └── lib/
│       └── logger.py          # Structured logging
├── resources/
│   ├── config.yaml            # Main configuration (API keys, model, switches)
│   ├── sources.yaml           # Regulatory source definitions
│   ├── analysis_prompt.md     # LLM prompt: analysis & tagging
│   ├── s1_web_prompt.md       # LLM prompt: web scraping strategy
│   ├── s1_rss_prompt.md       # LLM prompt: RSS parsing
│   ├── source_analysis_prompt.md
│   ├── steps/
│   │   ├── step_1.md          # Step 1 instruction
│   │   ├── step_2.md          # Step 2 instruction
│   │   ├── step_3.md          # Step 3 instruction
│   │   ├── step_4.md          # Step 4 instruction
│   │   └── step_5.md          # Step 5 instruction
│   └── templates/
│       ├── report.md          # Full report template
│       ├── report_group.md    # Group-level section template
│       └── report_item.md     # Single-item section template
└── gxpcode_data/
    ├── history.json           # Persistent dedup history
    └── logs/
        └── run_YYYYMMDD.log   # Per-run execution logs
```

---

## Dependencies

| Dependency | Purpose |
|-----------|---------|
| Python 3.10+ | Runtime |
| Playwright | Browser automation for JS-rendered pages (CDE) |
| PyYAML | Config & source definition loading |
| Requests / httpx | HTTP requests (API / RSS / web scraping) |
| Jinja2 | Template rendering (report assembly) |
| Markdown | Markdown to PDF conversion |
| LLM API (configurable) | AI analysis, summarization, tagging |

Quick install:

```bash
pip install -r scripts/requirements.txt
playwright install chromium
```

Or run `python scripts/setup.py` which does both automatically.

---

## Configuration

Edit `resources/config.yaml` to set:

| Key | Description |
|-----|-------------|
| `model.provider` | LLM provider (e.g. `deepseek`, `openai`) |
| `model.name` | Model name |
| `model.api_key` | API key |
| `model.base_url` | API endpoint |
| `product_types` | Keyword-based product type matching rules |
| `batch.max_items` | Max entries per analysis batch (default: 20) |
| `notify.channels` | Notification channels to activate |

Edit `resources/sources.yaml` to add or remove regulatory data sources.

---

## Traffic-light Levels

| Color | Meaning | Rule |
|-------|---------|------|
| 🔴 **Red** | Action required | Regulation directly impacts your product / process |
| 🟡 **Yellow** | Attention needed | Indirect or potential impact — needs review |
| 🟢 **Green** | Informational | Relevant domain, but no immediate action needed |
| ⚪ **Gray** | Not applicable | Out of scope for current monitoring profile |

---

## Output Example

After a run, the report PDF is structured as:

```
┌────────────────────────────────────┐
│  Report Header                     │
│  Date · Coverage period · Sources  │
├────────────────────────────────────┤
│  Table of Contents                 │
├────────────────────────────────────┤
│  1. Source Overview                │
│     Sources scanned · Findings per │
│     source · Change statistics     │
├────────────────────────────────────┤
│  2. New & Changed Entries          │
│     Grouped by source · Each entry │
│     includes:                      │
│     ├─ Title & URL                 │
│     ├─ Date & Change Type          │
│     ├─ AI Summary                  │
│     ├─ Tags                        │
│     └─ Applicability + 🚦 Level    │
├────────────────────────────────────┤
│  3. Appendix: Full Checklist       │
│     All scanned entries listed     │
└────────────────────────────────────┘
```

---

## CHANGELOG

See [CHANGELOG.md](CHANGELOG.md) for version history.

Latest: **v1.0.0** (2026-06-25) — official release.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Author

**GxpCode-hezhong** — Pharmaceutical regulatory compliance tools.

- GitHub: [@Gxpcode-hezhong](https://github.com/Gxpcode-hezhong)
- Repository: [Gxpcode-tu-xingsun](https://github.com/Gxpcode-hezhong/Gxpcode-tu-xingsun)
