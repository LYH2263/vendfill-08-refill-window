# VendFill 售货机补货

按货道容量、库存与在途量计算缺口，生成不超缺口、非负的补货单。

技术栈：Python 3.12 / FastAPI / SQLAlchemy / PostgreSQL / Vue 3 / TypeScript / Vite

## 启动

```bash
docker compose up --build
```

| 服务 | 地址 |
| --- | --- |
| 前端 | http://localhost:4800 |
| API | http://localhost:9800 |
| API 文档 | http://localhost:9800/docs |
| Postgres | localhost:5449 |

健康检查：`GET http://localhost:9800/api/health`

## 使用说明

1. 在「点位」「货道」查看售货机布局与库存。
2. 在「销量」了解近期出货。
3. 打开「补货单」按缺口生成建议补货量。
4. 在「满仓」「汇总」查看已满货道与补货合计。

## 补货时段窗

- 每个点位可登记补货时段窗：一天内分钟数，半开区间 `[开始, 结束)`；两格皆空表示不限时段。
- 当前时刻在窗外时，生成补货单会失败（原因：不在补货时段），不新增补货单，页面仍展示最近一次成功单。
- 非法窗（结束不大于开始、越界、只填一端）拒绝保存，点位与单据保持改前。
- 初始种子点位的窗极窄且避开当前时刻，需先在「点位」页放宽窗界再生成补货单。

## 开发与测试

```bash
docker compose exec api pytest -q
```
