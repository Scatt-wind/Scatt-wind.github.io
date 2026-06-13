# workflows

## 职责
- GitHub Actions 工作流：push 到 `master` 时构建并部署 GitHub Pages
- 不处理：应用业务逻辑、本地开发服务

## 关键文件
| 文件 | 说明 |
|------|------|
| `deploy-pages.yml` | 安装依赖 → `build_static.py` → 上传 `dist/` → 部署 Pages |

## 对外接口
- 触发：`push` 到 `branch: master`
- 权限：`contents: read`、`pages: write`、`id-token: write`
- 并发：`group: pages`，`cancel-in-progress: true`

## 依赖关系
- **上游**：仓库 push 事件
- **下游**：`requirements.txt`、`scripts/build_static.py`、`dist/` 产物

## 修改时注意
- Pages 源须已在仓库 Settings 中设为 **GitHub Actions**（非 branch 部署）
- Python 版本当前为 `3.11`，与 README 建议环境一致
- 构建失败时检查 Actions 日志中 `build_static.py` 的渲染错误
- 部署 job 依赖 `build` job 的 `upload-pages-artifact`

## 子模块
无
