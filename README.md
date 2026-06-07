# SGH-BLOG · 个人博客

基于 Flask 的深色主题个人博客，支持 Markdown 文件发布、首页展示、文章详情阅读，以及带分类筛选与搜索的文章列表页。

## 技术栈与架构

- **语言 / 框架：** Python 3、Flask
- **模板：** Jinja2
- **内容：** Markdown + YAML Front Matter（`python-frontmatter` + `markdown`）
- **热加载：** 开发模式下 `watchdog` 监听 `content/` 目录变更
- **前端：** 原生 HTML / CSS / JavaScript（无额外前端框架）

```
first_blog/
├── content/                 # 文章源文件（按分类存放）
│   ├── 项目介绍/
│   ├── 生活随笔/
│   └── 踩坑记录/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── routes.py            # 路由
│   ├── posts.py             # 文章访问接口
│   ├── content_loader.py    # Markdown 扫描与渲染
│   ├── content_watcher.py   # 开发模式热加载
│   ├── static/
│   │   ├── css/style.css
│   │   ├── images/          # 站点级图片（头像、二维码等）
│   │   └── js/
│   └── templates/
├── requirements.txt
└── run.py
```

文章数据从 `content/` 目录下的 Markdown 文件自动加载，按 `date` 降序排列，未接入数据库。

## 快速启动

**前置要求：** Python 3.10+

```bash
conda create -n blog python=3.11
conda activate blog
pip install -r requirements.txt
python run.py
```

浏览器访问 `http://127.0.0.1:5000`。

## 发布新文章

1. 在对应分类目录下新建 `.md` 文件，例如 `content/踩坑记录/my-new-post.md`
2. 填写 Front Matter 和正文：

```markdown
---
title: 文章标题
date: 2026-06-07
excerpt: 列表页显示的摘要（可选，不填则自动截取正文）
tags: [Python, Flask]
slug: my-new-post   # 可选，默认使用文件名
---

正文支持 **Markdown** 语法。

![配图说明](./my-new-post/screenshot.png)
```

3. 图片放在文章同目录或子文件夹，使用相对路径引用（见上文示例）
4. 开发模式下保存文件后自动热加载，刷新页面即可看到更新

**分类目录：** `项目介绍` / `生活随笔` / `踩坑记录`

**文章 URL：** `/post/<slug>`

**图片 URL：** 自动映射为 `/content/<slug>/<相对路径>`

## Agent 上下文 / 开发者备注

### 当前状态

- ✅ Markdown 文件发布：按分类目录存放，启动时扫描加载
- ✅ 开发热加载：`content/` 下 `.md` 与图片变更后自动重新加载
- ✅ 文章图片：与 Markdown 同目录存放，详情页自适应展示
- ✅ 首页：默认展示最近 3 篇文章，卡片整卡可点击进入详情
- ✅ 文章详情页：沉浸式阅读、代码复制、上下篇导航
- ✅ 文章列表页（`/articles`）：分类胶囊筛选、关键词搜索、客户端分页
- ✅ 关于我、友情链接页面

### 核心约定

- 导航高亮通过模板变量 `active_nav` 控制（`home` / `articles` / `about` / `links` / `None`）
- 文章分类由 `content/` 下的子文件夹名决定，取值：`项目介绍`、`生活随笔`、`踩坑记录`
- `slug` 默认等于文件名（不含 `.md`），Front Matter 可显式覆盖
- 阅读时长 `reading_minutes` 可根据正文字数自动估算，也可在 Front Matter 中手动指定

### 近期变更

- 文章系统从 `posts.py` 硬编码迁移至 `content/` Markdown 文件
- 新增 `content_loader.py` 扫描渲染与 `content_watcher.py` 开发热加载
- 新增 `/content/<slug>/<path>` 路由，支持文章同目录图片引用
- 详情页新增 `.article-body img` 样式

### 已知问题 / TODOs

- 友情链接列表待扩充，目前已收录卡码笔记
- 生产环境部署时需确认 `content/` 目录随应用一同发布
