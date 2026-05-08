# Source Tutor (MVP)

一个用于**源码学习闭环**的命令行工具：读取本地 Python 源码，按 class / function 切分，并基于真实源码生成练习题，帮助验证是否真正理解代码。

## 功能

- 支持输入单文件或目录路径。
- 使用 AST 按 `class` / `def` 切分并记录起止行号。
- 规则生成题目（不依赖外部 LLM API）。
- 交互答题：支持 `hint` / `source` / `why(解释)` / `next` / `quit`。
- 学习记录保存到 `.source_tutor/session.json`。
- 复习模式优先展示错题与标记不懂题目。
- 预留 `LLMQuestionGenerator` 接口，后续可接 OpenAI / Claude / 本地模型。

## 项目结构

```text
source_tutor.py
source_tutor/
  ├─ models.py
  ├─ loader.py
  ├─ chunker.py
  ├─ question_generator.py
  ├─ session.py
  └─ cli.py
tests/
  └─ test_basic.py
```

## 快速开始

```bash
python source_tutor.py --path ./transformers/src/transformers/models/qwen3/modeling_qwen3.py
```

目录模式：

```bash
python source_tutor.py --path ./transformers/src/transformers/models/qwen3
```

复习模式：

```bash
python source_tutor.py review
```

## 交互命令

- `A/B/C/D`: 作答
- `hint`: 仅提示，不直接给答案
- `source`: 显示对应源码证据
- `why` 或 `解释`: 查看详细解释
- `next`: 跳到下一题
- `quit`: 退出并保存记录

## 防幻觉规则（内置）

- 所有答案解释都绑定 `evidence`（文件路径 + 行号 + 代码片段）。
- 无法直接从片段判断时，使用：`无法从当前源码片段可靠判断`。
- 解释中明确注明源码依据行号。
- 需要推断时，明确标注：`这是基于源码的推断`。

## 运行测试

```bash
python -m pytest -q
```

> 若环境未安装 pytest，可先执行 `pip install pytest`。

## 后续扩展建议

- 增加跨文件调用链分析（调用图）。
- 增加概念标签抽取（attention / KV cache / RoPE 等）。
- 引入 spaced repetition 排序策略。
- 实现 Web UI（复用当前后端模块）。
