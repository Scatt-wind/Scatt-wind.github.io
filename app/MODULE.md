# app

## 职责
- Flask 博客应用核心：工厂创建、蓝图路由、Markdown 文章加载与开发热重载
- 不处理：静态站点构建（`scripts/`）、CI 配置（`.github/`）

## 关键文件
| 文件 | 说明 |
|------|------|
| `__init__.py` | `create_app()` 工厂；debug 下注册 `content_watcher` |
| `routes.py` | `main_bp` 蓝图，页面与内容资源路由 |
| `posts.py` | 文章访问门面，委托 `PostStore` |
| `content_loader.py` | 扫描 `content/`、解析 Front Matter、渲染 Markdown |
| `content_watcher.py` | `watchdog` 监听内容变更并 debounce 重载 |

## 对外接口
| 路由 | 处理函数 | 说明 |
|------|----------|------|
| `GET /` | `index` | 首页，最近 3 篇 |
| `GET /articles` | `articles` | 文章列表（全量传给模板，前端筛选分页） |
| `GET /about` | `about` | 关于我 |
| `GET /links` | `links` | 友情链接 |
| `GET /post/<slug>` | `post` | 文章详情，含上下篇 |
| `GET /content/<slug>/<path:filename>` | `content_asset` | 文章同目录图片等资源 |

**Python API（`posts.py`）：** `get_posts()`、`get_post_by_slug(slug)`、`get_asset_dir_for_slug(slug)`、`get_post_neighbors(slug)`

**Python API（`content_loader.py`）：** `get_post_store()`、`scan_posts()`、`CATEGORIES`

## 依赖关系
- **上游**：`run.py`、`scripts/build_static.py`（`create_app` + test_client）
- **下游**：`content/`（文章源）、`app/templates/`、`app/static/`、`markdown`、`python-frontmatter`、`watchdog`

## 修改时注意
- `CATEGORIES` 与 `content/` 子目录名必须一致：`项目介绍`、`生活随笔`、`踩坑记录`
- 文章 Front Matter 必填 `title`、`date`；缺一则跳过该文件
- `PostStore` 为进程内单例；热重载调用 `reload()`，非 debug 需重启进程
- 新增页面路由时同步更新 `scripts/build_static.py`
- `SECRET_KEY` 当前为开发占位值，生产静态站不依赖 session

## 子模块
- [templates/](templates/MODULE.md) — Jinja2 页面
- [static/](static/MODULE.md) — 前端静态资源
