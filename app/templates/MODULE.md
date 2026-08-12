# templates

## 职责
- Jinja2 页面模板：站点布局、各页面结构与数据绑定
- 不处理：业务逻辑、Markdown 渲染（由 `content_loader.py` 完成）

## 关键文件
| 文件 | 说明 |
|------|------|
| `base.html` | 全局布局：跳过链接、`SGH` 标识、中点导航、页脚，以及 jsDelivr 宋体 / 黑体 |
| `index.html` | 首页：开场「夜读，再写一行。」与最近 3 篇文章的无摘要墨线目录 |
| `articles.html` | 文章列表，嵌入 `data-*` 供 `articles.js` 筛选分页 |
| `post.html` | 窄栏文章详情：标题下红线、上下篇文字链，以及 KaTeX CDN 公式渲染 |
| `about.html` | 关于我：简介、能力磁贴 + 详情展开、爱好、邮件彩蛋 |
| `links.html` | 友情链接 |

## 对外接口
- 由 `app/routes.py` 的 `render_template()` 调用，无独立 HTTP 入口
- 模板变量：`active_nav`（`home` / `articles` / `about` / `links` / `None`）、`posts`、`categories`、`post` 等

## 依赖关系
- **上游**：`app/routes.py`
- **下游**：`app/static/`（`url_for('static', ...)`）、KaTeX CDN（仅 `post.html`）

## 修改时注意
- 导航链接使用 `url_for('main.*')`；静态构建后路径为相对 HTML 文件结构
- `articles.html` 列表项需保留 `data-category`、`data-title`、`data-excerpt`、`data-tags` 供 JS 使用
- 页面专属脚本通过 `{% block scripts %}` 扩展 `base.html`
- `post.html` 在 DOMContentLoaded 后调用 `renderMathInElement` 渲染 `.article-body` 内公式，依赖 jsDelivr KaTeX CDN
- `about.html` 依赖 `static/images/avatar.png` 与 `static/js/about.js`；能力详情文案写在 `#skill-detail-*` 的 `<template>` 中
- `base.html` 依赖 `static/images/wechat-qr.png`

## 子模块
无（叶子目录）
