---
name: csmar-proxy-download
description: 在已获授权且已配置本地代理和账号的前提下，通过浏览器自动化提交 CSMAR 数据下载请求，并核验收到的 Excel 压缩包是否完整。仅作为归档参考，不自动安装或执行。
metadata:
  short-description: CSMAR authorized download workflow reference
---

# CSMAR 代理下载参考

这是从 Workbuddy personal kit 迁入的归档技能。它记录了 CSMAR 网页端批量下载中最有价值的操作经验：选择子表全部字段、每次重新勾选邮箱投递、关闭提交窗口、收集临时下载链接，以及用 `openpyxl` 检查字段完整性。

## 使用边界

- 仅在用户拥有合法数据库访问权、代理服务使用权和邮箱权限时使用；不要绕过机构授权或服务条款。
- 本技能默认不安装、不自动登录、不保存账号、密码、验证码、邮箱授权码或下载链接。
- CSMAR 和第三方代理的页面、入口与授权状态会变化。运行前先人工确认当前页面和服务条款，再调整选择器与标签页定位。
- 不要把真实邮箱写入脚本。需要投递邮箱时，在本地配置并在运行前注入 `CSMAR_DOWNLOAD_EMAIL`，或直接在浏览器中填写。

## 推荐流程

1. 人工登录已获授权的入口，确认本地代理和 Playwright 会话正常。
2. 在 CSMAR 中选择目标子表，先执行“全选”字段，再勾选“下载结果发送至邮箱”。切换子表后邮箱复选框可能重置，必须重新确认。
3. 提交下载请求后关闭新开的提交窗口；不要把提交窗口误认为数据已下载完成。
4. 从用户自己的邮箱客户端或既有邮件工具提取下载链接，去重并在有效期内下载。
5. 使用 `scripts/verify_integrity.py` 扫描目标目录，检查压缩包中的首个 `.xlsx` 的字段数、行数和前几个表头。

## 参考资料

- 数据库与入口清单：阅读 [references/database_catalog.md](references/database_catalog.md)，但以当前授权页面为准。
- 页面结构和已知陷阱：阅读 [references/technical_notes.md](references/technical_notes.md)。
- 下载后核验：运行 [scripts/verify_integrity.py](scripts/verify_integrity.py)。它只读取压缩包并在目标目录写入 `integrity_report.json`。

## 迁入说明

原始批量 Playwright 脚本没有直接迁入：它包含个人邮箱、固定 `pages[2]` 标签页假设和随第三方页面变化的脆弱选择器。需要重新使用时，应先复制为本地工作脚本，改用环境变量或交互输入，并先对当前页面做小范围验证。
