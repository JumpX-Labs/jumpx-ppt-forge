<!-- 谢谢 PR！请简要填写下面几项，方便审阅。 -->

## 改了什么

<!-- 一句话说明 -->

## 影响哪一层

- [ ] `SKILL.md`（管线 / 门禁 / 铁律）
- [ ] `references/`（角色行为）
- [ ] `schemas/`（契约——已同步 references + scripts？）
- [ ] `scripts/`（校验 / 门禁，保持纯 stdlib）
- [ ] `assets/`（风格 preset / CSS / 样例）
- [ ] `docs/` / 其他文档

## 自检

- [ ] 跑过 `python3 scripts/validate_html.py … --json` 且 `errors: []`
- [ ] 跑过 `validate_slide_plan.py` / `validate_context_lock.py`（如相关）
- [ ] 未提交密钥（`.env`）或生成产物（`runs/`）
- [ ] 改了契约则同步更新了 references 与 scripts

## 备注 / 截图
