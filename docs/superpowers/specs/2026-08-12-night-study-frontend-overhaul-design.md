# 前端视觉重做：夜读书房

日期：2026-08-12  
状态：待用户确认 spec 后写实现计划

## 背景

站点是 Flask + Jinja + 原生 CSS/JS，经 `scripts/build_static.py` 预渲染后部署到 GitHub Pages。现有外观接近 GitHub Primer：`#0d1117` 底、`#58a6ff` 强调色、系统字体、卡片 + hover 上浮、首页渐变大标题。

用户要求：保持静态、不换框架、布局可以动。已选定方向「夜读书房」，实现策略是「设计系统 + 只改首页和文章页结构；其余页面换皮」。

已装入项目、实现时要遵守的 skill：

- `.cursor/skills/frontend-design/SKILL.md`
- `.cursor/skills/web-design-guidelines/SKILL.md`

## 目标

- 全站换成夜读书房视觉：靛蓝底、暖纸字、印章红只作短线/当前态。
- 首页：一句开场 + 墨线目录。
- 文章页：窄栏夜读。
- 补齐静态站质量底线：跳过链接、可见焦点、`prefers-reduced-motion`。
- 继续用现有静态构建部署到 GitHub Pages。

## 非目标

- 不上 React / Vue / Tailwind / 新 SSG。
- 不改 Flask 路由、Markdown 内容、`build_static.py` 的输出约定。
- 不改关于页文案、磁贴 `data-skill`、`about.js` 交互（见另份简历文案 spec）。
- 不改 `articles.js` 的筛选 / 搜索 / 分页逻辑与 `data-*` 约定。
- 不引入 Google Fonts（国内不稳定）；字体走 jsDelivr，与 KaTeX 同一 CDN。
- 不把简历 docx 纳入构建。

## 已确认选择

| 项 | 选择 |
|----|------|
| 改动幅度 | 布局可动的视觉重做 |
| 审美 | 夜读书房（非工位夜班、非浅色杂志） |
| 首页结构 | 一句开场 + 墨线目录 |
| 文章结构 | 窄栏夜读（标题下短红线） |
| 开场文案 | 夜读，再写一行。 |
| 实现策略 | 设计系统 + 只动首页/文章页结构 |

## 设计系统

### 色板

| Token | Hex | 用途 |
|-------|-----|------|
| `--bg-primary` | `#12151c` | 页面底 |
| `--bg-secondary` | `#181c24` | 顶栏、页脚 |
| `--text-primary` | `#f3ebe1` | 标题、正文 |
| `--text-secondary` | `#9a8f82` | 副文、导航默认 |
| `--text-muted` | `#8a7f72` | 日期、分类、元信息 |
| `--accent` | `#8b3a2f` | 印章红：短线、当前导航、最新一篇左边线 |
| `--border` | `#2c3340` | 分割、墨线默认 |

禁止再使用现有 GitHub 蓝 `#58a6ff`、紫渐变、卡片大圆角 + 上浮阴影作为主交互反馈。

### 字体

- 标题 / 开场句：Noto Serif SC（jsDelivr）
- 导航、正文、UI：Noto Sans SC（jsDelivr）
- 代码块：保持现有等宽栈
- 只加载实际用到的字重（约 400 / 600 / 700），`font-display: swap`

### 标志性元素

全站只大胆这一处：

- 标题下一条短印章红线（约 28–40px）
- 列表项左侧竖线：最新/当前用 `--accent`，其余用 `--border`

不做渐变标题、不做 01/02/03 编号、不做装饰性印章图片。

### 质量底线

- `base.html` 在 header 前加「跳到正文」，目标为 `<main>`
- 可聚焦控件有可见 `:focus-visible`（印章红或暖纸描边）
- `@media (prefers-reduced-motion: reduce)` 关掉非必要 transition / transform
- 现有图片保持 `width`/`height` 与有意义的 `alt`（头像、微信码）
- 顶栏滚动模糊可保留，但 reduced-motion 时改为纯色

## 各页面

### `base.html`

- Logo 文案改为 `SGH`（不再用 `SGH-BLOG`）
- 导航：`主页 · 文章 · 关于 · 友链`，间隔用中点，不用 `|`
- 当前项：底部短红线，不用蓝色下划线
- 页脚：保留 GitHub、微信二维码；去掉圆形按钮上浮；版权行用 `--text-muted`
- 在 `<head>` 引入上述字体；`main` 保留以便跳过链接

### 首页 `index.html`

- 开场 H1：`夜读，再写一行。`
- 副行：`技术笔记 · 生活随笔`（不是「欢迎来到我的个人博客」）
- 去掉 `.post-card` 卡片结构
- 「最新文章」三篇为墨线列表：日期、分类、标题；首页不展示摘要，避免再长成卡片
- 第一篇左边线用印章红，其余用 `--border`

### 文章页 `post.html`

- 阅读栏约 680px（现有 `container-article` 可收到这个宽度）
- 标题宋体 + 短红线；摘要保留但字重/字号低于标题
- 元信息：日期 · 分类 · 阅读时长，用 `--text-muted`；作者名可保留
- 正文行高约 1.75；链接用暖纸色 + 红线 hover，不用 GitHub 蓝
- 代码块、引用、表格改到新底色，对比度可读
- 上一篇 / 下一篇改为墨线文字链，去掉 `.nav-card` 大方块
- KaTeX CDN、`post.js` 返回逻辑不动

### 文章列表 `articles.html`

- 分类 pill、搜索框、空状态、分页、`data-category` / `data-title` / `data-excerpt` / `data-tags` **全部保留**
- `articles.js` 不动
- 列表项视觉改成墨线：日期 + 分类 + 标题为主；摘要一行、弱化
- pill / 搜索框换新色板，不要圆角胶囊的 GitHub 感过重；形状可略收，但点击区域和 JS 钩子不变

### 关于我 `about.html`

- 只换皮：侧栏 + 磁贴网格 + 详情展开结构不动
- 不改简介、磁贴文案、`data-skill`、`#skill-detail-*`、邮箱、头像
- `about.js` 不动
- 视觉跟新 token；磁贴去掉上浮，选中态用短红线或边框色，不用蓝

与 `docs/superpowers/specs/2026-08-12-about-page-resume-update-design.md` 的关系：那份 spec 改文案、本 spec 改外观。两份都落地时，文案以简历 spec 与 `tests/test_about.py` 为准；本 spec 不得覆盖那些字符串。

### 友链 `links.html`

- 文案与链接地址不动
- 去掉卡片上浮；改成墨线条目（站名 + 一句描述）

## 改动文件

| 路径 | 动作 |
|------|------|
| `app/templates/base.html` | 跳过链接、logo、导航分隔、字体 |
| `app/templates/index.html` | 开场文案 + 墨线列表 |
| `app/templates/post.html` | 窄栏结构、上下篇改为文字链 |
| `app/templates/articles.html` | 列表项 markup 可简化为墨线，保留 `data-*` |
| `app/templates/about.html` | 原则上不改 markup；若必须加 class，不得改文案与 `data-skill` |
| `app/templates/links.html` | 去卡片化，保留链接 |
| `app/static/css/style.css` | 重写 token 与上述组件样式 |
| `app/static/js/*.js` | 不动（`main.js` 顶栏 scrolled 可保留） |
| `scripts/build_static.py` | 不动 |
| `.github/workflows/deploy-pages.yml` | 不动 |
| `tests/test_about.py` | 不动；实现后必须仍通过 |
| README / 相关 `MODULE.md` | 仅当外观描述与现状不符时改一句 |

## 错误处理与测试

无新 API、无新表单。验证：

1. `python -m unittest`：关于页测试全过（本变更不得改文案断言）。
2. 本地跑站：首页三篇墨线、文章页窄栏 + 公式仍渲染、文章列表筛选/搜索/分页仍可用、关于页磁贴仍展开收起、友链可点。
3. 键盘：Tab 能看到焦点；跳过链接能进 `main`。
4. 系统开「减少动态效果」时，卡片/顶栏无明显位移动画。
5. `python scripts/build_static.py` 成功；`dist/` 仍是静态 HTML/CSS/JS；字体与 KaTeX 仍指向 jsDelivr。
6. 窄屏（≤600px）：导航不挤爆；关于页侧栏仍可叠成单栏；文章页左栏方案不存在（已否决书眉批注）。

## 风险

- jsDelivr 字体失败时须有系统宋体/无衬线回退，页面仍可读。
- 改 `articles.html` 列表 markup 时漏掉 `data-*` 会弄坏筛选；改完必须手测搜索与分类。
- 关于页若顺手改了文案，会与简历 spec / `test_about.py` 冲突。
- 首页去掉摘要后，卡片相关 CSS 可删，但文章列表若仍输出 excerpt，样式要单独弱化，不要两套卡片残留。
