# static

## 职责
- 站点级静态资源：全局样式、页面交互脚本、头像与二维码等图片
- 不处理：文章配图（由 `content/` + `/content/<slug>/` 路由提供）

## 关键文件
| 文件 | 说明 |
|------|------|
| `css/style.css` | 深色主题全局样式 |
| `js/main.js` | 全站：导航栏滚动态 |
| `js/articles.js` | 文章列表：分类筛选、搜索、客户端分页（每页 5 条） |
| `js/post.js` | 详情页：返回、表格横向滚动包裹、代码块复制 |
| `js/about.js` | 关于页：Chart.js 技能雷达图 |
| `images/avatar.png` | 关于页头像（模板引用） |
| `images/wechat-qr.png` | 页脚微信二维码（模板引用） |

## 对外接口
- Flask：`/static/<path>`（`url_for('static', filename=...)`）
- 静态构建：整目录复制到 `dist/static/`

## 依赖关系
- **上游**：`app/templates/`（引用）、`scripts/build_static.py`（复制到 `dist/`）
- **下游**：无后端依赖；`about.js` 依赖 Chart.js CDN

## 修改时注意
- 无构建工具链，改 CSS/JS 后刷新或重新运行 `build_static.py` 即可
- 新增页面脚本应在对应模板 `{% block scripts %}` 中引入，避免全局加载
- 文章正文样式主要在 `.article-body` 选择器下扩展

## 子模块
- `css/`、`js/`、`images/` — 按类型存放，无独立逻辑
