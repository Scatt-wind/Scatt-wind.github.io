# content

## 职责
- 博客文章源数据：按分类存放 Markdown 与同级/子目录配图
- 不处理：HTML 渲染、路由（由 `app/content_loader.py` 与 `app/routes.py` 负责）

## 关键文件
| 路径 | 说明 |
|------|------|
| `项目介绍/*.md` | 项目类文章 |
| `生活随笔/*.md` | 随笔类文章 |
| `踩坑记录/*.md` | 踩坑记录类文章 |
| `<文章目录>/` | 与 `.md` 同名的子文件夹可放配图（如 `RAVDA-.../主页图.png`） |

## 对外接口
- 无直接 API；经加载后映射为：
  - 文章页：`/post/<slug>`
  - 配图：`/content/<slug>/<相对路径>`（Markdown 内 `./` 相对路径会自动改写）

## 依赖关系
- **上游**：作者手动新增/编辑 `.md` 与图片
- **下游**：`app/content_loader.py`（扫描渲染）、`app/content_watcher.py`（开发热重载）、`scripts/build_static.py`（复制非 `.md` 资源到 `dist/content/`）

## 修改时注意
- 分类目录名须与 `app/content_loader.py` 中 `CATEGORIES` 一致
- Front Matter 必填：`title`、`date`；可选：`excerpt`、`tags`、`slug`、`reading_minutes`
- `slug` 默认为文件名（不含 `.md`）；同名子目录用于存放该文图片
- Markdown 图片使用相对路径，如 `![](./screenshot.png)`；外链与 `/static/` 路径不会被改写
- 仅扫描各分类目录下**直接**的 `*.md`，不递归子目录找文章文件

## 子模块
- `项目介绍/`、`生活随笔/`、`踩坑记录/` — 分类容器，结构相同
