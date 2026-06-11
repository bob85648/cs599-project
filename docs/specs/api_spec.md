# API Spec: TravelMind 内部接口

## 1. 环境变量

| 名称 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `LLM_API_KEY` | 是 | 空 | OpenAI 兼容模型服务 API Key |
| `LLM_MODEL_NAME` | 否 | `mimo-v2.5-pro` | 模型名称 |
| `LLM_BASE_URL` | 否 | `https://token-plan-cn.xiaomimimo.com/v1` | 模型服务地址 |
| `LLM_TEMPERATURE` | 否 | `0.7` | 生成温度 |
| `LLM_MAX_TOKENS` | 否 | `8192` | 最大输出 token |
| `LLM_TIMEOUT` | 否 | `60` | 请求超时时间 |
| `EMBEDDING_MODEL_PATH` | 否 | `data/models/bge-small-zh-v1.5` | 本地 embedding 模型路径 |

## 2. IntentionAgent 输出协议

输入：`agentscope.message.Msg` 或 `List[Msg]`，最后一条为用户 Query。

输出：`Msg.content` 为 JSON 字符串。

```json
{
  "reasoning": "用户意图分析过程",
  "intents": [
    {
      "type": "itinerary_planning",
      "confidence": 0.95,
      "description": "规划未来行程",
      "reason": "用户明确提出出差目的地和时间"
    }
  ],
  "key_entities": {
    "origin": "上海",
    "destination": "北京",
    "date": "2026-06-20",
    "duration": "3天",
    "other": "预算有限"
  },
  "rewritten_query": "用户希望规划从上海到北京的三天企业差旅行程，预算有限。",
  "agent_schedule": [
    {
      "agent_name": "event_collection",
      "priority": 1,
      "reason": "补全出行要素",
      "expected_output": "出发地、目的地、时间、目的"
    },
    {
      "agent_name": "rag_knowledge",
      "priority": 1,
      "reason": "查询企业差旅制度",
      "expected_output": "住宿标准和报销规则"
    },
    {
      "agent_name": "itinerary_planning",
      "priority": 2,
      "reason": "基于前序信息生成行程",
      "expected_output": "完整差旅方案"
    }
  ]
}
```

## 3. OrchestrationAgent 输入协议

输入：IntentionAgent 生成的 JSON 字符串。

关键字段：

- `agent_schedule`: 调度数组。
- `rewritten_query`: 标准化 Query。
- `key_entities`: 结构化实体。
- `intents`: 意图数组。

执行规则：

- 按 `priority` 升序执行。
- 同一 `priority` 内使用并行执行。
- 每个 Agent 的结果加入 `previous_results`，供后续 Agent 使用。

## 4. Skill Agent 约定

每个 Skill 至少包含：

```text
.claude/skills/<skill-name>/
├── SKILL.md
└── script/agent.py
```

`SKILL.md` frontmatter：

```yaml
---
name: plan-trip
description: 生成企业差旅行程方案
---
```

`script/agent.py` 需暴露可被懒加载注册器实例化的 Agent 类。Agent 接收上下文后返回 JSON 或自然语言结果。

## 5. CLI 命令

| 命令 | 行为 |
| --- | --- |
| `python cli.py` | 启动交互式差旅助手 |
| `python cli.py health` | 执行 LLM 健康检查 |
| `help` | 查看交互式命令 |
| `status` | 查看当前会话状态 |
| `history` | 查看历史行程 |
| `preferences` | 查看用户偏好 |
| `clear` | 清空当前任务上下文 |
| `exit` | 退出 |
