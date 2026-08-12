# About Page Resume Copy Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update `/about` copy to match the 2026 resume (intro, five skill tiles, details, 163 email) without adding intern/education sections.

**Architecture:** Keep the existing Jinja template + `about.js` click-to-expand pattern. Content lives only in `app/templates/about.html` (`data-skill` buttons + `#skill-detail-*` templates). Add a Flask test-client check so the new copy and forbidden old strings are asserted on `GET /about`.

**Tech Stack:** Flask 3, Jinja2, existing `about.js`, stdlib `unittest` (no new dependency).

## Global Constraints

- Do not add internship, company, education, or phone-as-contact to the page.
- Email on the about page must be `13208281328@163.com` (not `honglanh6765@gmail.com`).
- Display name stays `SGH`; tagline and hobbies stay unchanged.
- Do not edit `app/static/js/about.js`, `app/static/css/style.css`, or `app/templates/base.html`.
- Do not invent metrics absent from the resume (no Dify/Coze/MCP, 95%+, 召回率 90%+, 8.3×, -62%, 20 万级, +40%).
- `data-skill` values must match `<template id="skill-detail-{id}">` exactly (`about.js` concatenates `skill-detail-` + `data-skill`).
- Skill ids: `rag`, `agent`, `classify`, `compress`, `prompt`.
- Do not git commit unless the user explicitly asks; skip commit steps until then.
- Do not add the resume `.docx` to the site or git unless already tracked.

---

## File Structure

- `tests/test_about.py` — Flask test client assertions for `/about` copy
- `tests/MODULE.md` — module doc for the new test directory
- `app/templates/about.html` — only production file to change (intro, tiles, templates, email)

No new routes, CSS, or JS.

---

### Task 1: Failing about-page content tests

**Files:**
- Create: `tests/test_about.py`
- Create: `tests/MODULE.md`
- Modify: none yet

**Interfaces:**
- Consumes: `app.create_app()` → Flask app; `GET /about` via test client
- Produces: `unittest` module `tests.test_about` with `AboutPageTest`

- [ ] **Step 1: Write the failing test**

Create `tests/test_about.py`:

```python
import re
import unittest

from app import create_app

INTRO = (
    "2 年大模型应用开发，方向是 RAG / Agent。"
    "做过不合格描述分类、质量标准知识库问答、异常多轮排查 Agent。"
)

SKILL_TILES = (
    ("rag", "RAG", "FAQ 命中 92%+ · 答对率 88%"),
    ("agent", "Agent", "LangGraph · 最多 8 轮"),
    ("classify", "文本分类", "BERT 94% · F1 0.93"),
    ("compress", "模型压缩", "量化 / 蒸馏 / 剪枝"),
    ("prompt", "Prompt + AI 编程", "Bad Case 迭代 · Cursor"),
)

FORBIDDEN = (
    "Dify",
    "Coze",
    "智能投顾",
    "金融资讯",
    "honglanh6765@gmail.com",
    "召回率 90%",
    "8.3",
    "20 万级",
    "1.5 年",
    "广东特拓",
    "广州软件学院",
)


class AboutPageTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def _html(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        return response.get_data(as_text=True)

    def test_intro_matches_resume_summary(self):
        html = self._html()
        self.assertIn(INTRO, html)

    def test_email_is_163_not_gmail(self):
        html = self._html()
        self.assertIn("13208281328@163.com", html)
        self.assertNotIn("honglanh6765@gmail.com", html)
        phone_hits = re.findall(r"13208281328(?!@163\.com)", html)
        self.assertEqual(phone_hits, [])

    def test_keeps_name_tagline_and_hobbies(self):
        html = self._html()
        self.assertIn("SGH", html)
        self.assertIn("用代码解决问题，用文字记录生活", html)
        self.assertIn("CS2 双平台 S 分段", html)
        self.assertIn("软笔书法（国家十级）", html)
        self.assertIn("打篮球", html)

    def test_skill_tiles_and_templates_align(self):
        html = self._html()
        for skill_id, title, metric in SKILL_TILES:
            self.assertIn(f'data-skill="{skill_id}"', html)
            self.assertIn(f'id="skill-detail-{skill_id}"', html)
            self.assertIn(title, html)
            self.assertIn(metric, html)
        self.assertNotIn('data-skill="deploy"', html)
        self.assertNotIn('data-skill="data"', html)

    def test_skill_details_include_resume_facts(self):
        html = self._html()
        self.assertIn("FAQ 命中准确率 92%+", html)
        self.assertIn("整体答对率从 75% 提到 88%", html)
        self.assertIn("LangGraph", html)
        self.assertIn("最多 8 轮", html)
        self.assertIn("BERT 准确率 94%、F1 0.93", html)
        self.assertIn("学生模型是 BiLSTM", html)
        self.assertIn("Cursor、Claude Code", html)

    def test_old_copy_and_employer_are_absent(self):
        html = self._html()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, html)


if __name__ == "__main__":
    unittest.main()
```

Create `tests/MODULE.md`:

```markdown
# tests

## 职责
- 用 Flask 测试客户端校验页面文案与约定
- 不处理：浏览器 UI 交互（磁贴展开由 `about.js` 负责，本目录不做 JS 测试）

## 关键文件
| 文件 | 说明 |
|------|------|
| `test_about.py` | `GET /about`：简介、邮箱、磁贴 id、简历事实、旧文案不得出现 |

## 对外接口
- `python -m unittest tests.test_about -v`

## 依赖关系
- **上游**：开发者本地 / 后续 CI（若接入）
- **下游**：`app.create_app()`、`app/templates/about.html`

## 修改时注意
- 关于页文案变更时同步改本测试中的期望字符串
- 禁止把简历里的公司名、学历写进断言的「应出现」列表

## 子模块
无
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m unittest tests.test_about -v
```

Expected: FAIL. `test_intro_matches_resume_summary` (and likely others) because current `about.html` still has `1.5 年` / Gmail / Dify copy. Failures must be assertion failures on missing new copy or present old copy, not `ImportError` / app factory errors.

- [ ] **Step 3: Skip commit**

Do not commit unless the user asks.

---

### Task 2: Replace about.html copy

**Files:**
- Modify: `app/templates/about.html` (intro, skill grid, templates, email; keep sidebar/hobbies/scripts)

**Interfaces:**
- Consumes: `about.js` looks up `#skill-detail-` + `data-skill`; tiles stay `button.about-skill-tile`
- Produces: `/about` HTML that satisfies `tests.test_about`

- [ ] **Step 1: Confirm tests still fail before editing production template**

Run:

```bash
python -m unittest tests.test_about -v
```

Expected: still FAIL (same reasons as Task 1 Step 2).

- [ ] **Step 2: Write minimal implementation**

In `app/templates/about.html`:

1. Replace the intro paragraph with:

```html
                <p class="about-intro">
                    2 年大模型应用开发，方向是 RAG / Agent。做过不合格描述分类、质量标准知识库问答、异常多轮排查 Agent。
                </p>
```

2. Replace the entire `.about-skill-grid` + `#about-skill-detail` + five `<template>` blocks with:

```html
                <div class="about-skill-grid" role="list">
                    <button
                        type="button"
                        class="about-skill-tile"
                        role="listitem"
                        data-skill="rag"
                        aria-expanded="false"
                        aria-controls="about-skill-detail"
                    >
                        <span class="about-skill-tile-title">RAG</span>
                        <span class="about-skill-tile-metric">FAQ 命中 92%+ · 答对率 88%</span>
                    </button>
                    <button
                        type="button"
                        class="about-skill-tile"
                        role="listitem"
                        data-skill="agent"
                        aria-expanded="false"
                        aria-controls="about-skill-detail"
                    >
                        <span class="about-skill-tile-title">Agent</span>
                        <span class="about-skill-tile-metric">LangGraph · 最多 8 轮</span>
                    </button>
                    <button
                        type="button"
                        class="about-skill-tile"
                        role="listitem"
                        data-skill="classify"
                        aria-expanded="false"
                        aria-controls="about-skill-detail"
                    >
                        <span class="about-skill-tile-title">文本分类</span>
                        <span class="about-skill-tile-metric">BERT 94% · F1 0.93</span>
                    </button>
                    <button
                        type="button"
                        class="about-skill-tile"
                        role="listitem"
                        data-skill="compress"
                        aria-expanded="false"
                        aria-controls="about-skill-detail"
                    >
                        <span class="about-skill-tile-title">模型压缩</span>
                        <span class="about-skill-tile-metric">量化 / 蒸馏 / 剪枝</span>
                    </button>
                    <button
                        type="button"
                        class="about-skill-tile"
                        role="listitem"
                        data-skill="prompt"
                        aria-expanded="false"
                        aria-controls="about-skill-detail"
                    >
                        <span class="about-skill-tile-title">Prompt + AI 编程</span>
                        <span class="about-skill-tile-metric">Bad Case 迭代 · Cursor</span>
                    </button>
                </div>

                <div
                    id="about-skill-detail"
                    class="about-skill-detail"
                    aria-live="polite"
                >
                    <p class="about-skill-detail-placeholder">点击上方能力查看详情</p>
                    <div class="about-skill-detail-body" hidden>
                        <h3 class="about-skill-detail-title"></h3>
                        <p class="about-skill-detail-desc"></p>
                    </div>
                </div>

                <template id="skill-detail-rag">
                    <span data-title>RAG</span>
                    <span data-desc>FAQ 高置信就直接返回，没命中再走向量检索 + 生成。文档按章节切块，表格尽量整块留；做过 PDF 父子分块，大约 2000 块，BGE-M3 写入 Milvus。检索按零件、文档类型、缺陷类型过滤，跨件误召回降了大约 40%。FAQ 命中准确率 92%+，误命中压在 3% 以内；自建 120 题评测，整体答对率从 75% 提到 88%。生成侧用 LangChain 接 Qwen，要求强制引用，标准数值不够就拒答。</span>
                </template>
                <template id="skill-detail-agent">
                    <span data-title>Agent</span>
                    <span data-desc>用 LangGraph 做多轮排查：接案、查槽位、追问或调工具、出建议、结案。下一步按槽位和规则走，不是写死流水线；同一 case 跨轮合并槽位，最多 8 轮。尺寸类缺测量值就强制追问，不给硬结论。工具有分类建议、标准检索、相似案例检索。有证据才给排查建议，并写明只辅助、不替代判废；证据都没有就转人工，不编数据。对外是 FastAPI 接口，另外有 CLI demo。</span>
                </template>
                <template id="skill-detail-classify">
                    <span data-title>文本分类</span>
                    <span data-desc>不合格现象是自由文本，先归到外观、尺寸、装配、功能这几类。样本 5000 条（训练 4000 / 测试 1000）。对比过 TF-IDF + 随机森林、FastText、BERT。BERT 准确率 94%、F1 0.93，比随机森林基线（F1 0.82）高 11 个百分点。</span>
                </template>
                <template id="skill-detail-compress">
                    <span data-title>模型压缩</span>
                    <span data-desc>在 BERT 上做过动态量化、蒸馏（学生模型是 BiLSTM）和 L1 剪枝。效果和体积一起看，更倾向蒸馏到 BiLSTM，当轻量部署的备选。</span>
                </template>
                <template id="skill-detail-prompt">
                    <span data-title>Prompt + AI 编程</span>
                    <span data-desc>Prompt 会写指令约束、输出格式和角色，也会加上引用要求和拒答条件，按 Bad Case 小步改。开发上用 Cursor、Claude Code 拆需求、改代码、定位报错，主要用来加速 Agent / RAG / 分类相关模块。</span>
                </template>
```

3. In the ASCII easter egg, replace `honglanh6765@gmail.com` with `13208281328@163.com`. Keep the box width readable; the new address is longer, so adjust padding spaces so the `✉` line still fits inside the `║` borders (widen the box if needed rather than wrapping the email).

4. Leave unchanged: `{% extends %}`, title, avatar, `SGH`, tagline, hobbies list, `{% block scripts %}` loading `about.js`.

Do not add sections titled 工作经历 / 教育经历 / 实习.

- [ ] **Step 3: Run test to verify it passes**

Run:

```bash
python -m unittest tests.test_about -v
```

Expected: `Ran 6 tests` / `OK`. If `test_old_copy_and_employer_are_absent` fails on `8.3`, search `about.html` for leftover `8.3×`. If phone regex fails, ensure the number only appears inside `13208281328@163.com`.

- [ ] **Step 4: Manual / static check**

- Open `/about` in the running app (or `python scripts/build_static.py` then inspect `dist/about/index.html`).
- Click each of the five tiles: title + detail appear; click again to collapse.
- Confirm README.md and `app/templates/MODULE.md` still describe the page as 简介 + 磁贴 + 爱好 + 邮件彩蛋 (no old metrics). Do not rewrite them unless a stale specific claim appears.

- [ ] **Step 5: Skip commit**

Do not commit unless the user asks.

---

## Spec coverage (self-review)

| Spec item | Task |
|-----------|------|
| New intro, no company/应届/金融 | Task 2 intro + Task 1 `test_intro_*` / `FORBIDDEN` |
| Email 163, no phone contact | Task 2 easter egg + Task 1 `test_email_*` |
| Five tiles + details + new ids | Task 2 grid/templates + Task 1 tile/detail tests |
| Keep SGH, tagline, hobbies, JS/CSS | Task 1 keep test; Task 2 leave those blocks |
| No intern/education sections | Task 2 explicit omit + FORBIDDEN employer/school |
| Drop old metrics | Task 1 `FORBIDDEN` + Task 2 new copy only |
| README/MODULE check | Task 2 Step 4 |
| `about.js` data-skill pairing | Task 1 `test_skill_tiles_and_templates_align` |
