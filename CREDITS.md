# Credits & Attribution

本 Skill 在设计与实现上参考、致谢以下来源：

## 字体（运行环境提供，非内置）

deck 通过 CSS font-stack 调用、由渲染环境提供，**不内置字体文件**：

- **Noto Sans SC / Source Han Sans** — © Google / Adobe，[SIL Open Font License 1.1](https://scripts.sil.org/OFL)。
- 其余系统兜底字体（PingFang SC / Microsoft YaHei / Hiragino Sans GB）归各操作系统所有。

## 设计与方法

- 视觉风格的取向（编辑杂志 / 瑞士网格 / 蓝图 / 手绘 等）参考了对应设计传统与公开范式；具体的 preset token 与参考 CSS 为本项目自行编写。
- 管线"门禁 + 角色分工 + 设计 token 锁定"的思路，受多家"AI 做 deck"实践与 deepagents/HITL 范式启发。

## 历史说明

- 早期版本曾内置一组 HTML 模板片段（vendored samples）；自 **v1.0.0**「彻底移除模板渲染器」起，这些模板已删除，渲染改为模型按 token 直接写 HTML。当前仓库不再分发第三方模板代码。

> 若你发现任何应被署名而未署名的来源，请提 Issue，我们会补上。
