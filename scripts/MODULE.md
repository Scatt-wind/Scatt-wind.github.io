# scripts

## 职责
- 将 Flask 应用预渲染为静态 HTML，供 GitHub Pages 托管
- 不处理：运行时服务、文章内容编写

## 关键文件
| 文件 | 说明 |
|------|------|
| `build_static.py` | 主构建脚本，输出到 `dist/` |

## 对外接口
- 命令：`python scripts/build_static.py`
- 输出目录：`dist/`
  - 页面：`index.html`、`articles/index.html`、`about/index.html`、`links/index.html`、`post/<slug>/index.html`
  - 资源：`static/`、`content/<slug>/`（文章配图）
  - 其他：`.nojekyll`、`404.html`（复制自首页）

## 依赖关系
- **上游**：本地开发者、`.github/workflows/deploy-pages.yml`
- **下游**：`app.create_app`、`app.posts`（test_client 预渲染）、`app/static/`、`content/` 配图

## 修改时注意
- 新增**固定页面**路由须加入 `STATIC_ROUTES` 列表
- 动态文章路由由 `get_posts()` 循环生成，一般无需改 `STATIC_ROUTES`
- 构建时设置 `app.config["TESTING"] = True`，不启动 `content_watcher`
- 非 200 响应会抛 `RuntimeError` 导致构建失败
- 本地预览：`cd dist && python -m http.server 8080`

## 子模块
无（叶子目录）
