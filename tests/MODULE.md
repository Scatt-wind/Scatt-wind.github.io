# tests

## 职责
- 用 Flask 测试客户端校验页面文案与约定
- 不处理：浏览器 UI 交互（磁贴展开由 `about.js` 负责，本目录不做 JS 测试）

## 关键文件
| 文件 | 说明 |
|------|------|
| `test_about.py` | `GET /about`：简介、邮箱、磁贴 id、简历事实、旧文案不得出现 |
| `test_night_study.py` | Night Study 前端契约：skip-link、ink-list、CSS token、字体 CDN、JS hooks |

## 对外接口
- `python -m unittest tests.test_about -v`
- `python -m unittest tests.test_night_study -v`

## 依赖关系
- **上游**：开发者本地 / 后续 CI（若接入）
- **下游**：`app.create_app()`、`app/templates/about.html`

## 修改时注意
- 关于页文案变更时同步改本测试中的期望字符串
- 禁止把简历里的公司名、学历写进断言的「应出现」列表

## 子模块
无
