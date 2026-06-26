# first_blog

## 职责
- 项目根：Flask 个人博客（SGH-BLOG）的入口与模块索引
- 提供开发服务器（`run.py`）与 GitHub Pages 静态发布流水线
- 不负责：文章内容创作细节（见 `content/`）、页面样式实现（见 `app/static/`）

## 关键文件
| 文件 | 说明 |
|------|------|
| `run.py` | 开发入口，`create_app()` + `debug=True` |
| `requirements.txt` | Python 依赖 |
| `README.md` | 面向人类的安装、部署与发文指南 |

## 对外接口
- 开发：`python run.py` → `http://127.0.0.1:5000`
- 静态构建：`python scripts/build_static.py` → 输出 `dist/`
- 线上：https://scatt-wind.github.io/

## 依赖关系
- **上游**：开发者、GitHub Actions（`deploy-pages.yml`）
- **下游**：`app/`（应用）、`content/`（文章源）、`scripts/`（构建）

## 修改时注意
- 无数据库；文章数据全部来自 `content/` Markdown 扫描
- 生产部署走静态预渲染，新增路由须同步更新 `scripts/build_static.py` 的 `STATIC_ROUTES` 或文章循环
- 人类文档见 [README.md](README.md)

## 模块索引
| 路径 | 职责摘要 |
|------|----------|
| `app/` | Flask 应用工厂、路由、Markdown 渲染（内链/公式/图片）与热重载 |
| `app/templates/` | Jinja2 页面模板 |
| `app/static/` | CSS、JS、站点图片 |
| `content/` | Markdown 文章源文件与配图 |
| `scripts/` | GitHub Pages 静态预渲染构建 |
| `.github/workflows/` | push 到 `master` 时自动部署 Pages |
