# Night Study Frontend Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the static Flask blog into the Night Study look (indigo, warm paper type, seal-red rules) with a new home list and narrow article column, without changing the GitHub Pages static pipeline.

**Architecture:** Keep Jinja templates + one global `style.css` + existing page JS. Lock new class names in tests first (`skip-link`, `#main`, `.ink-list` / `.ink-item`, `.article-title-rule`, `.article-nav-link`). Swap CSS tokens and restyle remaining pages in place. `articles.js` / `about.js` / `post.js` stay untouched.

**Tech Stack:** Flask 3, Jinja2, vanilla CSS/JS, jsDelivr fonts (Noto Serif SC / Noto Sans SC), existing `unittest` + `scripts/build_static.py`.

## Global Constraints

- Stay static HTML/CSS/JS. No React, Vue, Tailwind, or new SSG.
- Do not edit `app/static/js/main.js`, `articles.js`, `about.js`, or `post.js`.
- Do not edit `scripts/build_static.py` or `.github/workflows/deploy-pages.yml`.
- Do not change about-page copy, `data-skill`, or `#skill-detail-*` (that is `2026-08-12-about-page-resume-update-design.md`).
- Do not add Google Fonts. Fonts and KaTeX stay on `cdn.jsdelivr.net`.
- Palette (verbatim): `--bg-primary #12151c`, `--bg-secondary #181c24`, `--text-primary #f3ebe1`, `--text-secondary #9a8f82`, `--text-muted #8a7f72`, `--accent #8b3a2f`, `--border #2c3340`.
- Home H1 copy (verbatim): `夜读，再写一行。` Subline: `技术笔记 · 生活随笔`.
- Logo text is `SGH` (not `SGH-BLOG`). Nav separators are `·` (not `|`).
- Home latest posts: date + category + title only (no excerpt). First item gets `ink-item--latest`.
- Article reading column ≈ 680px. Prev/next are text links, not `.nav-card`.
- `articles.html` must keep `data-category`, `data-title`, `data-excerpt`, `data-tags`, and class `article-item`.
- Do not git commit unless the user explicitly asks; skip commit steps until then.
- Follow `.cursor/skills/frontend-design/SKILL.md` and `.cursor/skills/web-design-guidelines/SKILL.md` while implementing.

---

## File Structure

- `tests/test_night_study.py` — Flask client assertions for shell, home, post, articles hooks, CSS tokens
- `tests/MODULE.md` — add the new test module
- `app/templates/base.html` — skip link, fonts, logo, nav dots, `#main`
- `app/templates/index.html` — hero copy + ink list
- `app/templates/post.html` — title rule + prev/next text links
- `app/templates/articles.html` — drop inner card wrapper; keep `article-item` + `data-*`
- `app/templates/links.html` — ink entries (same URLs/copy)
- `app/templates/about.html` — do not modify
- `app/static/css/style.css` — tokens, type, ink list, article column, restyle pills/about/links, a11y
- `app/templates/MODULE.md`, `app/static/MODULE.md`, `README.md` — one-line description updates if they still say GitHub-blue / card UI

No new routes. No new JS files.

---

### Task 1: Failing Night Study tests

**Files:**
- Create: `tests/test_night_study.py`
- Modify: `tests/MODULE.md`

**Interfaces:**
- Consumes: `app.create_app()` → Flask app; `GET /`, `/articles`, `/about`, `/links`, `/static/css/style.css`
- Produces: `unittest` module `tests.test_night_study` with `NightStudyFrontendTest`

- [ ] **Step 1: Write the failing test**

Create `tests/test_night_study.py`:

```python
import unittest

from app import create_app

HERO = "夜读，再写一行。"
HERO_SUB = "技术笔记 · 生活随笔"
TOKENS = {
    "--bg-primary": "#12151c",
    "--bg-secondary": "#181c24",
    "--text-primary": "#f3ebe1",
    "--text-secondary": "#9a8f82",
    "--text-muted": "#8a7f72",
    "--accent": "#8b3a2f",
    "--border": "#2c3340",
}


class NightStudyFrontendTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def _get(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        return response.get_data(as_text=True)

    def test_base_shell_has_skip_link_logo_and_dot_nav(self):
        html = self._get("/")
        self.assertIn('class="skip-link"', html)
        self.assertIn('href="#main"', html)
        self.assertIn('id="main"', html)
        self.assertIn(">SGH</a>", html)
        self.assertNotIn("SGH-BLOG", html)
        self.assertIn("·", html)
        self.assertNotIn('class="nav-sep" aria-hidden="true">|</span>', html)
        self.assertIn("cdn.jsdelivr.net", html)
        self.assertIn("noto-serif-sc", html.lower())
        self.assertIn("noto-sans-sc", html.lower())
        self.assertNotIn("fonts.googleapis.com", html)

    def test_home_uses_ink_list_not_cards(self):
        html = self._get("/")
        self.assertIn(HERO, html)
        self.assertIn(HERO_SUB, html)
        self.assertNotIn("欢迎来到我的个人博客", html)
        self.assertIn('class="ink-list"', html)
        self.assertIn("ink-item--latest", html)
        self.assertNotIn("post-card", html)

    def test_article_page_is_narrow_night_read(self):
        home = self._get("/")
        marker = 'class="ink-item-link"'
        self.assertIn(marker, home)
        href_start = home.index("href=\"", home.index(marker)) + 6
        href_end = home.index("\"", href_start)
        post_path = home[href_start:href_end]
        html = self._get(post_path)
        self.assertIn('class="article-title-rule"', html)
        self.assertIn("article-nav-link", html)
        self.assertNotIn("nav-card", html)

    def test_articles_list_keeps_js_hooks(self):
        html = self._get("/articles")
        self.assertIn("article-item", html)
        self.assertIn("data-category=", html)
        self.assertIn("data-title=", html)
        self.assertIn("data-excerpt=", html)
        self.assertIn("data-tags=", html)
        self.assertIn('id="articles-search"', html)
        self.assertIn('id="pagination"', html)
        self.assertNotIn("article-item-card", html)

    def test_links_keep_existing_target(self):
        html = self._get("/links")
        self.assertIn("https://notes.kamacoder.com", html)
        self.assertIn("卡码笔记", html)

    def test_css_tokens_match_night_study(self):
        css = self._get("/static/css/style.css")
        for name, value in TOKENS.items():
            self.assertIn(name, css)
            self.assertIn(value, css)
        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertNotIn("--accent: #58a6ff", css)


if __name__ == "__main__":
    unittest.main()
```

In `tests/MODULE.md`, add a row for `test_night_study.py` and mention `python -m unittest tests.test_night_study -v`. Keep the about-page notes.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_night_study -v`

Expected: FAIL (missing skip-link / `夜读，再写一行。` / `--accent: #8b3a2f`).

- [ ] **Step 3: Skip implementation in this task**

Do not edit templates or CSS yet. Later tasks make these tests pass.

- [ ] **Step 4: Commit (only if the user asked)**

```bash
git add tests/test_night_study.py tests/MODULE.md
git commit -m "test: add Night Study frontend contract checks"
```

---

### Task 2: Tokens, fonts, skip link, nav shell

**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/static/css/style.css` (token block, body/type, header, skip-link, focus, reduced-motion)

**Interfaces:**
- Consumes: Task 1 assertions for shell + CSS tokens
- Produces: `skip-link`, `#main`, logo `SGH`, nav `·`, jsDelivr Noto faces, Night Study tokens

- [ ] **Step 1: Confirm font CSS URLs return 200**

Run:

```bash
python -c "import urllib.request; urls=['https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-400.css','https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-700.css','https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc@5.2.5/chinese-simplified-400.css','https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc@5.2.5/chinese-simplified-600.css'];
[print(u, urllib.request.urlopen(u).status) for u in urls]"
```

Expected: four `200`. If a URL 404s, drop the version pin (`@5.2.5`) or use the latest 5.x that exists; do not switch to `fonts.googleapis.com`.

- [ ] **Step 2: Update `base.html`**

Replace the `<head>` and chrome with:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}个人博客{% endblock %}</title>
    <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc@5.2.5/chinese-simplified-400.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc@5.2.5/chinese-simplified-600.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-400.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.2.5/chinese-simplified-700.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="{% block body_class %}{% endblock %}">
    <a class="skip-link" href="#main">跳到正文</a>
    <header class="site-header">
        <div class="container">
            <a href="/" class="logo">SGH</a>
            <nav class="nav">
                <a href="{{ url_for('main.index') }}" class="nav-link{% if active_nav == 'home' %} active{% endif %}">主页</a>
                <span class="nav-sep" aria-hidden="true">·</span>
                <a href="{{ url_for('main.articles') }}" class="nav-link{% if active_nav == 'articles' %} active{% endif %}">文章</a>
                <span class="nav-sep" aria-hidden="true">·</span>
                <a href="{{ url_for('main.about') }}" class="nav-link{% if active_nav == 'about' %} active{% endif %}">关于我</a>
                <span class="nav-sep" aria-hidden="true">·</span>
                <a href="{{ url_for('main.links') }}" class="nav-link{% if active_nav == 'links' %} active{% endif %}">友情链接</a>
            </nav>
        </div>
    </header>

    <main id="main" class="main-content">
        <div class="container {% block container_class %}{% endblock %}">
            {% block content %}{% endblock %}
        </div>
    </main>
```

Keep the existing footer (GitHub + WeChat QR + copyright). Do not change SVG paths or `main.js` include.

- [ ] **Step 3: Replace CSS tokens and add a11y + type**

In `app/static/css/style.css`, replace the `:root` block with:

```css
:root {
    --bg-primary: #12151c;
    --bg-secondary: #181c24;
    --bg-card: #181c24;
    --bg-hover: #1e232c;
    --text-primary: #f3ebe1;
    --text-secondary: #9a8f82;
    --text-muted: #8a7f72;
    --accent: #8b3a2f;
    --accent-hover: #a24a3c;
    --border: #2c3340;
    --tag-bg: #1a1514;
    --tag-text: #d4b4a8;
    --shadow: rgba(0, 0, 0, 0.35);
    --font-sans: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
    --font-serif: "Noto Serif SC", "Songti SC", "SimSun", serif;
}
```

Update `body` `font-family` to `var(--font-sans)`. Set default `a { color: var(--text-primary); }` and hover to `var(--accent)` (no GitHub blue).

Add immediately after the reset:

```css
.skip-link {
    position: absolute;
    left: 12px;
    top: -48px;
    z-index: 200;
    padding: 8px 12px;
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--accent);
}

.skip-link:focus {
    top: 12px;
}

:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

.logo {
    font-family: var(--font-serif);
    font-weight: 700;
}

.nav-sep {
    color: var(--text-muted);
    opacity: 1;
}

.nav-link.active {
    border-bottom-color: var(--accent);
}

.site-header.is-scrolled {
    background-color: rgba(24, 28, 36, 0.84);
    border-bottom-color: var(--border);
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }

    .site-header.is-scrolled {
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
    }
}
```

Remove the gradient from `.hero-title` (plain `--text-primary`, serif) even if home markup is still old — Task 3 replaces markup next.

- [ ] **Step 4: Run shell/token tests**

Run: `python -m unittest tests.test_night_study.NightStudyFrontendTest.test_base_shell_has_skip_link_logo_and_dot_nav tests.test_night_study.NightStudyFrontendTest.test_css_tokens_match_night_study -v`

Expected: those two PASS. Home/post/articles tests may still FAIL.

- [ ] **Step 5: Commit (only if the user asked)**

```bash
git add app/templates/base.html app/static/css/style.css
git commit -m "style: add Night Study tokens, fonts, and skip link"
```

---

### Task 3: Home — opening line + ink list

**Files:**
- Modify: `app/templates/index.html`
- Modify: `app/static/css/style.css` (hero + posts section)

**Interfaces:**
- Consumes: `posts` from `app/routes.py` `get_posts()[:3]` (unchanged)
- Produces: `.ink-list` / `.ink-item` / `.ink-item--latest` / `.ink-item-link`; first item red rule

- [ ] **Step 1: Replace `index.html` content block**

```html
{% extends "base.html" %}

{% block title %}主页 - 个人博客{% endblock %}

{% block content %}
<section class="hero">
    <h1 class="hero-title">夜读，再写一行。</h1>
    <p class="hero-subtitle">技术笔记 · 生活随笔</p>
</section>

<section class="posts">
    <h2 class="section-title">最新文章</h2>
    <div class="ink-list">
        {% for post in posts %}
        <article class="ink-item{% if loop.first %} ink-item--latest{% endif %}">
            <a href="{{ url_for('main.post', slug=post.slug) }}" class="ink-item-link">
                <div class="ink-item-meta">
                    <time datetime="{{ post.date }}">{{ post.date }}</time>
                    <span class="ink-item-category">{{ post.category }}</span>
                </div>
                <h3 class="ink-item-title">{{ post.title }}</h3>
            </a>
        </article>
        {% endfor %}
    </div>
</section>
{% endblock %}
```

No excerpt on the home list.

- [ ] **Step 2: Replace hero/card CSS with ink-list CSS**

Remove `.post-card`, `.post-card-link`, `.post-card:hover`, `.post-excerpt` home usage. Keep `.post-meta` / `.post-tag` only if still used elsewhere; otherwise delete.

Add:

```css
.hero {
    text-align: left;
    padding: 24px 0 40px;
    border-bottom: none;
    margin-bottom: 32px;
}

.hero-title {
    font-family: var(--font-serif);
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 10px;
    letter-spacing: 0.02em;
    color: var(--text-primary);
    background: none;
    -webkit-text-fill-color: unset;
}

.hero-title::after {
    content: "";
    display: block;
    width: 36px;
    height: 1px;
    margin-top: 14px;
    background: var(--accent);
}

.hero-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.section-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: none;
    color: var(--text-muted);
    margin-bottom: 16px;
}

.ink-list {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.ink-item {
    border-left: 2px solid var(--border);
    padding: 12px 0 12px 16px;
}

.ink-item--latest {
    border-left-color: var(--accent);
}

.ink-item-link {
    display: block;
    color: inherit;
    text-decoration: none;
}

.ink-item-meta {
    display: flex;
    gap: 12px;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 4px;
}

.ink-item-title {
    font-family: var(--font-serif);
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-primary);
}

.ink-item-link:hover .ink-item-title {
    color: var(--accent);
}
```

- [ ] **Step 3: Run home tests**

Run: `python -m unittest tests.test_night_study.NightStudyFrontendTest.test_home_uses_ink_list_not_cards -v`

Expected: PASS.

- [ ] **Step 4: Commit (only if the user asked)**

```bash
git add app/templates/index.html app/static/css/style.css
git commit -m "feat: restyle homepage as Night Study ink list"
```

---

### Task 4: Article page — narrow night read

**Files:**
- Modify: `app/templates/post.html` (header rule + footer nav only; keep KaTeX block and `post.js`)
- Modify: `app/static/css/style.css` (article header/footer)

**Interfaces:**
- Consumes: `post`, `prev_post`, `next_post` from `app/routes.py` (unchanged)
- Produces: `.article-title-rule`, `.article-nav-link` / `-prev` / `-next`, `.article-nav-empty`

- [ ] **Step 1: Update article header and footer markup**

In `app/templates/post.html`, keep the back button and `article-body`. Change header + footer to:

```html
<header class="article-header">
    <h1 class="article-title">{{ post.title }}</h1>
    <div class="article-title-rule" aria-hidden="true"></div>
    <p class="article-excerpt">{{ post.excerpt }}</p>
    <div class="article-meta">
        <time datetime="{{ post.date }}">{{ post.date }}</time>
        <span class="meta-sep">·</span>
        <span class="article-author">Scattwind</span>
        <span class="meta-sep">·</span>
        <span class="article-tags">
            {% for tag in post.tags %}
            <span class="article-tag">{{ tag }}</span>
            {% endfor %}
        </span>
        <span class="meta-sep">·</span>
        <span class="article-reading-time">预计阅读 {{ post.reading_minutes }} 分钟</span>
    </div>
</header>
```

```html
<footer class="article-footer">
    <div class="article-nav">
        {% if prev_post %}
        <a href="{{ url_for('main.post', slug=prev_post.slug) }}" class="article-nav-link article-nav-link-prev">
            <span class="article-nav-label">上一篇</span>
            <span class="article-nav-title">{{ prev_post.title }}</span>
        </a>
        {% else %}
        <div class="article-nav-empty"></div>
        {% endif %}

        {% if next_post %}
        <a href="{{ url_for('main.post', slug=next_post.slug) }}" class="article-nav-link article-nav-link-next">
            <span class="article-nav-label">下一篇</span>
            <span class="article-nav-title">{{ next_post.title }}</span>
        </a>
        {% else %}
        <div class="article-nav-empty"></div>
        {% endif %}
    </div>

    <p class="article-feedback">
        对本文有建议或想法？欢迎发邮件至
        <a href="mailto:honglanh6765@gmail.com">honglanh6765@gmail.com</a>
    </p>
</footer>
```

Do not change the KaTeX `<link>`/`<script>` block or `post.js`. Do not change the feedback email in this task (about-page email change is a different spec).

- [ ] **Step 2: Restyle article column**

```css
.page-post .container,
.container-article {
    max-width: 680px;
}

.article-header {
    text-align: left;
    margin-bottom: 40px;
    padding-bottom: 28px;
    border-bottom: 1px solid var(--border);
}

.article-title {
    font-family: var(--font-serif);
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.01em;
    line-height: 1.35;
    margin-bottom: 12px;
}

.article-title-rule {
    width: 36px;
    height: 1px;
    background: var(--accent);
    margin: 0 0 16px;
}

.article-excerpt {
    font-size: 0.95rem;
    color: var(--text-secondary);
    max-width: none;
    margin: 0 0 16px;
}

.article-meta {
    color: var(--text-muted);
    justify-content: flex-start;
}

.article-body {
    line-height: 1.75;
}

.article-nav {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 32px;
}

.article-nav-link {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 8px 0 8px 12px;
    border-left: 2px solid var(--border);
    color: inherit;
}

.article-nav-link:hover {
    border-left-color: var(--accent);
    color: inherit;
}

.article-nav-link-next {
    text-align: right;
    padding: 8px 12px 8px 0;
    border-left: none;
    border-right: 2px solid var(--border);
}

.article-nav-link-next:hover {
    border-right-color: var(--accent);
}

.article-nav-label {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.article-nav-title {
    font-family: var(--font-serif);
    font-size: 0.95rem;
    color: var(--text-primary);
}

.article-nav-empty {
    visibility: hidden;
}
```

Delete `.nav-card*` rules so `nav-card` no longer appears in CSS. Keep code-copy / KaTeX / article-body typography, but retint borders to `--border` and links in `.article-body a` to `--accent`.

Remove or gate `.article { animation: fadeIn }` behind the reduced-motion block (already global).

- [ ] **Step 3: Run article tests**

Run: `python -m unittest tests.test_night_study.NightStudyFrontendTest.test_article_page_is_narrow_night_read -v`

Expected: PASS.

- [ ] **Step 4: Commit (only if the user asked)**

```bash
git add app/templates/post.html app/static/css/style.css
git commit -m "feat: restyle article page as narrow Night Study column"
```

---

### Task 5: Articles list, about tiles, links — restyle only

**Files:**
- Modify: `app/templates/articles.html` (drop `.article-item-card` wrapper only)
- Modify: `app/templates/links.html` (class names; same href/copy)
- Modify: `app/static/css/style.css` (pills, timeline, about tiles, links)
- Do not modify: `app/templates/about.html`, any `app/static/js/*`

**Interfaces:**
- Consumes: `articles.js` selectors `.article-item`, `.tag-pill`, `#articles-search`, `#pagination`, `#articles-empty`, `data-*`
- Produces: same JS hooks; visual ink list; links still `https://notes.kamacoder.com`

- [ ] **Step 1: Flatten articles list markup**

Replace the inner card with:

```html
<article
    class="article-item"
    data-category="{{ post.category }}"
    data-title="{{ post.title }}"
    data-excerpt="{{ post.excerpt }}"
    data-tags="{{ post.tags | join(' ') }}"
>
    <a href="{{ url_for('main.post', slug=post.slug) }}" class="article-item-link">
        <div class="article-item-meta">
            <time datetime="{{ post.date }}">{{ post.date }}</time>
            <span class="article-item-category">{{ post.category }}</span>
        </div>
        <h2 class="article-item-title">{{ post.title }}</h2>
        <p class="article-item-excerpt">{{ post.excerpt }}</p>
    </a>
</article>
```

Keep toolbar, empty state, pagination, and the `articles.js` script block unchanged.

- [ ] **Step 2: Restyle list / pills / about / links**

Articles list: remove the vertical timeline dots (`::before` on `.articles-timeline` and `.article-item`). Style `.article-item` like `.ink-item` (left border, no card, no translateY). First visible item does not need `--latest` (filter/paging would make it lie). Excerpt: one muted line.

Pills / search: no 999px capsule and no blue gradient.

```css
.tag-pill {
    border-radius: 2px;
    background: transparent;
}

.tag-pill.active {
    color: var(--text-primary);
    background: transparent;
    border-color: var(--accent);
    box-shadow: none;
}

.articles-search-input {
    border-radius: 2px;
}

.articles-search-input:focus {
    box-shadow: 0 0 0 2px rgba(139, 58, 47, 0.35);
}

.articles-timeline::before,
.article-item::before {
    content: none;
    display: none;
}

.article-item {
    padding: 12px 0 12px 16px;
    border-left: 2px solid var(--border);
}

.article-item-link:hover .article-item-title {
    color: var(--accent);
}

.article-item-excerpt {
    color: var(--text-muted);
    font-size: 0.85rem;
}
```

About (CSS only): remove tile `transform` / heavy shadow; selected/hover uses `--accent` border. Keep `.about-skill-grid` layout.

Links: in `links.html` keep the same `<a href="https://notes.kamacoder.com" ...>` copy. Change classes to `ink-item` / `ink-item-title` / `ink-item-meta` if that is simpler, or restyle `.link-card` in place: no translateY, left border instead of filled card.

- [ ] **Step 3: Run remaining frontend tests plus about tests**

Run:

```bash
python -m unittest tests.test_night_study tests.test_about -v
```

Expected: `tests.test_night_study` all PASS.

`tests.test_about`: PASS if about copy was already updated; if it FAILs on old intro/email strings, do **not** change `about.html` copy in this plan — leave that to the resume spec. Only fix about tests if this task accidentally broke markup/`data-skill`.

- [ ] **Step 4: Commit (only if the user asked)**

```bash
git add app/templates/articles.html app/templates/links.html app/static/css/style.css
git commit -m "style: restyle articles, about, and links to Night Study ink rules"
```

---

### Task 6: Static build, docs, full verification

**Files:**
- Modify: `app/templates/MODULE.md` (home/post/base descriptions)
- Modify: `app/static/MODULE.md` (theme one-liner)
- Modify: `README.md` only if it still describes GitHub-blue cards as the look

**Interfaces:**
- Consumes: `python scripts/build_static.py` → `dist/`
- Produces: verified static output; docs that match the new chrome

- [ ] **Step 1: Update module docs**

`app/templates/MODULE.md`:

- `base.html`: 跳过链接、`SGH`、中点导航、jsDelivr 宋体/黑体
- `index.html`: 开场「夜读，再写一行。」+ 三篇墨线目录（无摘要）
- `post.html`: 窄栏、标题下红线、上下篇文字链
- Keep the `articles.html` `data-*` warning unchanged

`app/static/MODULE.md`: `css/style.css` 改为「夜读书房 token（靛蓝 / 暖纸 / 印章红）」.

- [ ] **Step 2: Run full unit tests**

Run: `python -m unittest discover -s tests -v`

Expected: `test_night_study` PASS. `test_about` as in Task 5.

- [ ] **Step 3: Build static site**

Run: `python scripts/build_static.py`

Expected: exit 0; `dist/` contains HTML. Spot-check `dist/index.html` for `夜读，再写一行。`, `skip-link`, `SGH`, and no `SGH-BLOG`. Spot-check a post HTML for `article-title-rule` and KaTeX jsDelivr URLs.

- [ ] **Step 4: Manual a11y sweep (required by spec)**

Locally open `/` (or `python -m http.server` in `dist`):

1. Tab: skip link appears, Enter moves to `#main`.
2. Tab through nav: `:focus-visible` ring visible.
3. Articles: category + search + pagination still work.
4. About: tiles still expand/collapse.
5. Optional: OS “reduce motion” on — header should not blur/slide.

- [ ] **Step 5: Commit (only if the user asked)**

```bash
git add app/templates/MODULE.md app/static/MODULE.md README.md
git commit -m "docs: describe Night Study chrome and ink-list home"
```

---

## Spec coverage (self-review)

| Spec item | Task |
|-----------|------|
| Palette tokens | 2 |
| Noto via jsDelivr, no Google Fonts | 2 |
| Skip link, focus-visible, reduced-motion | 2 |
| Logo `SGH`, nav `·` | 2 |
| Home copy + ink list, no excerpt, first item red | 3 |
| Article 680px, title rule, text prev/next | 4 |
| Articles `data-*` + `articles.js` untouched | 5 |
| About copy/JS untouched, tiles restyled | 5 |
| Links restyle, same URL | 5 |
| No React / no build script change | all |
| unittest + `build_static.py` | 1, 6 |
| README / MODULE.md | 6 |

No TBD/TODO placeholders. Class names used in later tasks match Task 1 tests (`skip-link`, `#main`, `ink-list`, `ink-item--latest`, `ink-item-link`, `article-title-rule`, `article-nav-link`).
