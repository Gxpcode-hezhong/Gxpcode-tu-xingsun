[English](README_EN.md) | [中文](README.md)
# GxpCode-Tu-Xingsun

> 制药法规自动跟踪系统 — 扫描 · 比对 · 分析 · 报告

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10+-green)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## 简介

**土行孙** 是一个制药法规跟踪 WorkBuddy Skill，自动扫描 NMPA / CDE / FDA / EMA / PIC/S 等 16 个法规源，发现新发布/修订/废止的法规与指南，通过 LLM 分析摘要并打标签，判断与企业产品的关联程度，最终生成 PDF 跟踪报告。

## 特性

- **16 个法规源**：覆盖中国 NMPA/CDE（14 个频道）、美国 FDA、欧盟 EMA、国际 PIC/S
- **双通道采集**：RSS（FDA/EMA）+ Playwright 浏览器自动化（CDE/NMPA/PIC/S）
- **智能去重**：基于 history.json 跨期判重，仅输出本期新增
- **LLM 分析**：自动摘要 + 标签（GMP/注册/变更...）+ 四级适用性判断
- **PDF 报告**：按适用性分组的结构化报告，含红/黄/绿/灰等级标记
- **容错设计**：FATAL / SOURCE_SKIP / ITEM_SKIP 三级容错，单源失败不影响整体

## 监控源

| 机构 | 源 | 类型 |
|------|-----|:---:|
| NMPA | 药品监管动态 / 公告通告 / 法规文件 / 综合监督检查 / 法规文件总览 / 法律行政法规 / 部门规章 / 行政规范性文件 / 工作文件 / 其他文件 | Web |
| CDE | 指导原则 / 征求意见 | Web |
| FDA | Drug Guidances | RSS |
| EMA | News | RSS |
| PIC/S | Publications | Web |

## 快速开始

### 环境配置（首次）

```bash
pip install -r scripts/requirements.txt
python scripts/setup.py
```

`setup.py` 会检查 Python 依赖并下载。

### 首次运行

1. WorkBuddy 中加载本 Skill
2. 触发关键词："法规跟踪" / "法规扫描" / "法规监控"
3. 首次运行自动进入对话式引导，配置企业类型和关注领域

### 后续使用

每次运行自动执行 5 步流水线，产出 PDF 报告。

## 工作流

```
用户触发 / 定时调度
    │
    ├─ 首次？→ setup.py 环境配置 → config.yaml 初始化
    │
    ▼
Step 1  检测  │  RSS + Web 采集  →  s1/*.json
Step 2  比对  │  与 history 去重  →  s2/*.json（仅新增）
Step 3  获取  │  详情页 + PDF附件  →  s3/*.json
Step 4  分析  │  LLM 摘要+标签+适用性  →  s4/*.json
Step 5  通知  │  生成 MD → 渲染 PDF  →  s5_report_*.pdf
```

## 报告示例

生成的 PDF 报告按适用性分组：

```
🔴 直接适用（3 条）
  ├─ 药品管理法实施条例（第4次修订）
  └─ 药物临床试验质量管理规范（GCP 2026修订版）

🟡 潜在相关（5 条）
  ├─ 斑秃治疗药物临床试验技术指导原则（征求意见稿）
  └─ 处方药网络零售合规指南政策解读

🟢 仅供参考（1 条）
⚪ 不适用（2 条）
⚠️ 待人工复核（1 条）
```

## 目录结构

```
GxpCode-tu-xingsun/
├── SKILL.md                    # Skill 定义
├── README.md                   # 本文件
├── CHANGELOG.md                # 变更日志
├── resources/
│   ├── config.yaml             # 用户配置（企业类型/关注领域）
│   ├── sources.yaml            # 法规源定义
│   ├── steps/                  # 各步骤详细 Prompt
│   ├── templates/              # 报告模板
│   └── *.md                    # 分析/源分析 Prompt
├── scripts/
│   ├── setup.py                # 一键环境配置
│   ├── step1_rss.py            # RSS 采集
│   ├── step1_web.py            # Web 浏览器采集
│   ├── step2_compare.py        # 历史比对去重
│   ├── step3_fetch.py          # 详情页 + PDF 下载
│   ├── step4_merge.py          # LLM 结果合并校验
│   ├── step5_notify.py         # 报告生成（MD + PDF）
│   ├── stepA_analyze.py        # 新源分析
│   ├── lib/logger.py           # 共享日志
│   └── requirements.txt        # Python 依赖
└── gxpcode_data/
    └── history.json            # 历史记录（212 条种子数据）
```

## 依赖

| 包 | 版本 | 用途 |
|----|------|------|
| feedparser | ≥6.0 | RSS 解析 |
| pyyaml | ≥6.0 | 配置文件读写 |
| markdown | ≥3.5 | MD → HTML |
| playwright | ≥1.40 | 浏览器自动化 + PDF 渲染 |

浏览器：Playwright Chromium（~400 MB，首次 `setup.py` 自动下载）

## 许可

MIT License
