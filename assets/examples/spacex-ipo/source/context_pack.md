# Context Pack — 上市的，不是火箭

| 维度 | 内容 |
|------|------|
| **Project Goal** | 用一份观点 deck 讲清：这场"史上最大 IPO"真正被定价的不是火箭，而是 Starlink 的经常性现金流 |
| **Audience** | 关注科技/投资的泛财经读者；想看懂这场 IPO 真正逻辑的人 |
| **Use Case** | 对外观点输出 / 演讲开场 / 社媒长图 |
| **Output Mode** | `html-only`（16:9，可本地打开/导出 PDF） |

## Knowledge Base（耐久结构性事实，避免编造 2026 精确数字）
- 火箭发射＝一次性收入，确认一次即到顶；Starlink 订阅＝经常性收入，按月复利累积。
- Starlink 是一张面向全球、覆盖 100+ 国家的卫星连接网络（公开量级，非精确数字）。
- SpaceX 垂直整合：自造火箭→压低发射成本→批量铺星座→直接向用户收月费，成本与收入在同一家公司闭环。
- 资本市场给"可预测的经常性现金流"更高估值倍数；电信/基础设施平台与航天承包商的估值锚不在一个量级。

## Narrative Direction
观点升华弧：Hook（反差）→ Reframe（搬走焦点）→ Core（讲透为什么）→ Moat（为什么抄不动）→ Shift（拔高一层）→ Takeaway（落地 + 记忆点）。

## Design Direction
`editorial-magazine`：暖纸底 + 墨色衬线大标题 + 单一品牌红 accent；封面与金句页用深色整页；数字/词当视觉锚。

## Tone Rules
讲立场、敢断言、克制；用比喻（发射台 vs 收费站）锚定认知；不堆术语。

## Forbidden Zones
- 不编造未经证实的 2026 精确财务数字（估值/营收/订户具体数）当事实；模型逻辑示意须标注。
- 不堆等大灰卡片网格；禁外链。

## Acceptance Criteria
- 6 页一屏放下、横向翻页可用；
- `validate_html.py --json` → `failed:false`；
- 论点清晰、有记忆点（"火箭负责上头条，Starlink 负责上财报"）。

## Style Preset
`editorial-magazine`
