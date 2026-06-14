# PersonOS Distill Mini

`distill-mini` 是 PersonOS 的行为蒸馏数据工厂 MVP。第一版只管理本地测试问题、
手工 teacher 答案、OpenAI student 答案、judge 对比结果，以及 SFT 数据导出。
除了 CLI，也提供一个本地流水线看板客户端。

当前版本刻意不包含微调、自动爬取、接口破解、任务队列或数据库。

## 项目结构

```text
tools/distill-mini/
├── data/
│   ├── inputs.jsonl
│   ├── teacher_outputs.jsonl
│   ├── student_outputs.jsonl
│   ├── comparisons.jsonl
│   └── dataset_sft.jsonl
├── src/distill_mini/
│   ├── clients/
│   │   ├── manual_client.py
│   │   └── openai_client.py
│   ├── static/
│   │   ├── app.css
│   │   ├── app.js
│   │   └── index.html
│   ├── cli.py
│   ├── config.py
│   ├── models.py
│   ├── prompts.py
│   ├── service.py
│   └── storage.py
├── .env.example
└── pyproject.toml
```

## 安装

需要 Python 3.11+。推荐使用 `uv`：

```bash
cd tools/distill-mini
uv sync
uv run personos-distill --help
```

也可以使用标准 `pip`：

```bash
cd tools/distill-mini
python -m venv .venv
source .venv/bin/activate
pip install -e .
personos-distill --help
```

## 配置 OpenAI

手工 teacher 录入和 SFT 导出不需要 API Key。student 生成与 judge 对比需要：

```bash
cp .env.example .env
```

然后在 `.env` 中填写 `OPENAI_API_KEY`，并按需修改模型名或
`OPENAI_BASE_URL`。未配置 API Key 时，OpenAI 相关命令会打印跳过原因并正常退出。

## 本地 Web 客户端

启动服务：

```bash
uv run personos-distill-web
```

然后访问 <http://127.0.0.1:8765>。看板按当前阶段将问题放入
`Inputs → Teacher → Student → Judged` 四列：

- 顶部按钮对当前已具备前置条件的问题批量运行 Student 或 Compare。
- 点击问题卡片，在右侧抽屉录入 Teacher 答案或运行单条任务。
- `导出 SFT` 会重建并下载 `dataset_sft.jsonl`。

## 使用流程

```bash
# 1. 添加测试问题
personos-distill add "测试问题"

# 2. 逐条手工录入 teacher output
personos-distill collect-teacher --mode manual

# 3. 调用配置的学生模型生成 student output
personos-distill collect-student

# 4. 使用 judge prompt 对比 teacher/student
personos-distill compare

# 5. 将已有 teacher output 导出成 chat-format SFT 数据
personos-distill export-sft
```

`collect-teacher`、`collect-student` 和 `compare` 默认只处理尚未有对应结果的输入，
因此可以安全地重复执行。`export-sft` 每次会重建 `data/dataset_sft.jsonl`。

## JSONL 数据约定

- `inputs.jsonl`：测试问题及唯一 ID。
- `teacher_outputs.jsonl`：手工录入的参考答案。
- `student_outputs.jsonl`：学生模型生成的答案。
- `comparisons.jsonl`：judge 模型的结构化对比结果。
- `dataset_sft.jsonl`：基于 teacher 答案导出的训练样本。

每行都是独立合法的 JSON 对象，便于审阅、版本管理和后续迁移。
