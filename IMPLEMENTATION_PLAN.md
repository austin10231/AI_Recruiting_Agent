# AI Recruiting Copilot Agent - Revised Implementation Plan (Strict Assignment Alignment)

## A. English Version

## 1) Recommended Project Architecture
Use a clear, modular, sequential pipeline with one orchestrator and five explicit step modules.

- Entry point is `python main.py`.
- `main.py` loads assignment input (Job Description required, Hiring Manager Notes optional), runs all 5 steps in order, and writes `output.json`.
- Each step is a separate code unit (separate file/function), with one visible LLM call per step.
- Step 4 has explicit in-code validation + retry loop (up to 3 attempts), not hidden.
- A shared `PipelineState` object passes outputs from each step to the next step.

Why this design:
- Reviewer can quickly verify assignment compliance.
- Keeps orchestration explicit and easy to audit.
- Looks agent-oriented without unnecessary framework complexity.

What NOT to do:
- Do not collapse all steps into one prompt/call.
- Do not hide retry logic in generic middleware.
- Do not build heavy framework layers that reduce readability.

---

## 2) Folder Structure

```text
AI_Recruiting_Agent/
  main.py
  requirements.txt
  README.md
  output.json

  app/
    orchestrator.py
    state.py
    llm_client.py

    steps/
      step1_extract_jd_signals.py
      step2_generate_search_strategy.py
      step3_generate_boolean_query.py
      step4_generate_outreach_message.py
      step5_generate_candidate_summary.py

    prompts/
      step1_prompt.txt
      step2_prompt.txt
      step3_prompt.txt
      step4_prompt.txt
      step5_prompt.txt

    validators/
      outreach_validator.py

    tracing/
      trace_utils.py

  data/
    input.json
```

Why:
- Minimal but complete.
- Step boundaries are obvious.
- Prompt and validator logic are visible and testable.

---

## 3) File-by-File Responsibilities

- `main.py`: parse input, initialize `PipelineState`, run orchestrator, serialize final `output.json`.
- `app/orchestrator.py`: strict sequential execution of steps 1→5; centralized error boundary.
- `app/state.py`: defines `PipelineState` (inputs, intermediate outputs, final outputs, trace).
- `app/llm_client.py`: thin wrapper for model call; no business logic.
- `app/steps/step1_extract_jd_signals.py`: Step 1 prompt + parse logic.
- `app/steps/step2_generate_search_strategy.py`: Step 2 prompt + parse logic.
- `app/steps/step3_generate_boolean_query.py`: Step 3 prompt + parse logic.
- `app/steps/step4_generate_outreach_message.py`: Step 4 generation + explicit validation + retry loop.
- `app/steps/step5_generate_candidate_summary.py`: Step 5 summary generation (uses pipeline artifacts and internal mock candidate list if needed).
- `app/prompts/*.txt`: one prompt per step.
- `app/validators/outreach_validator.py`: checks message length and JD detail inclusion.
- `app/tracing/trace_utils.py`: helper to append assignment-compatible trace entries.

---

## 4) Data Flow Between Pipeline Steps

Important input rule (strict):
- External input from assignment only includes:
  - Job Description (required)
  - Hiring Manager Notes (optional)
- There is NO external candidate profile input.

Sequential flow:
1. `extract_jd_signals`
   - Input: JD + optional manager notes
   - Output: structured role signals including role type, required skills, seniority indicators, company stage, and missing information flags
2. `generate_search_strategy`
   - Input: Step 1 output
   - Output: candidate search strategy
3. `generate_boolean_query`
   - Input: Step 1 + Step 2 outputs
   - Output: boolean query
4. `generate_outreach_message`
  - Input: Step 1 + Step 2 + Step 3 outputs
  - Output: outreach message (with retry/validation loop; personalized, startup-oriented, and non-generic tone)
5. `generate_candidate_summary`
   - Input: Step 1–4 outputs + internally generated mock candidate snippets (if needed)
   - Output: candidate summary

Notes for Step 5:
- If candidate-specific language is needed, mock candidate snippets are generated internally by pipeline logic (or directly within Step 5), not provided as external assignment input.

---

## 5) State Management Strategy

Use one simple `PipelineState` dataclass:

- `job_description`
- `hiring_manager_notes` (optional)
- `jd_signals`
- `candidate_search_strategy`
- `boolean_query`
- `outreach_message`
- `candidate_summary`
- `pipeline_trace` (list of trace objects)
- `internal_context` (for temporary values, including Step 5 internal mock candidate snippets if used)

Why:
- Explicit data ownership.
- Easy debugging.
- Easy reviewer verification of step-by-step chaining.

---

## 6) `pipeline_trace` Design (Strict Schema Alignment)

Each trace entry must keep required assignment fields exactly:

- `step` (integer: 1..5)
- `action`
- `attempt`
- `result`
- `note`

Required value rules from assignment:
- `step`: integer step number, not a string label
- `action`: must match one of the fixed step names:
  - `extract_jd_signals`
  - `generate_search_strategy`
  - `generate_boolean_query`
  - `generate_outreach_message`
  - `generate_candidate_summary`
- `result`: only `pass` or `retry` or `fail`
- Step 4 must log each attempt (attempt 1/2/3 entries as applicable)

Submission-safe recommendation:
- Keep `pipeline_trace` objects limited to required fields only.
- Store extra observability (timestamps/duration/model/validation detail) in a separate internal debug log file if needed.

If you intentionally include optional trace metadata, keep it under nested `metadata` only. Example:

```json
{
  "step": 4,
  "action": "generate_outreach_message",
  "attempt": 2,
  "result": "retry",
  "note": "Failed validation: exceeded 300 characters",
  "metadata": {
    "duration_ms": 412,
    "validation": {
      "length_ok": false,
      "has_jd_detail": true
    }
  }
}
```

What NOT to do:
- Do not replace required keys with custom names.
- Do not flatten metadata into top-level required fields.
- Do not let optional metadata break evaluator parsing expectations.

---

## 7) `output.json` Schema Design (Strict Top-Level Alignment)

Top-level keys must be exactly:

- `candidate_search_strategy`
- `boolean_query`
- `outreach_message`
- `candidate_summary`
- `pipeline_trace`

No additional top-level keys should be added for submission safety.

Field-level structure must also match assignment schema:

1. `candidate_search_strategy` (object)
- `target_backgrounds`: list[string]
- `target_companies`: list[string]
- `keywords`: list[string]
- `seniority`: string

2. `boolean_query` (object)
- `boolean_query`: string

3. `outreach_message` (object)
- `outreach_message`: string (strictly < 300 chars)
- `specific_detail`: string (exact JD phrase used for personalization)
- `character_count`: integer
- `attempts`: integer

4. `candidate_summary` (object)
- `name`: string (mock is acceptable)
- `current_company`: string
- `key_skills`: list[string] (3 to 5)
- `fit_reason`: string
- `concerns`: string

5. `pipeline_trace` (list[object])
- each object uses required keys: `step/action/attempt/result/note`

Recommended output shape:

```json
{
  "candidate_search_strategy": {
    "target_backgrounds": [],
    "target_companies": [],
    "keywords": [],
    "seniority": ""
  },
  "boolean_query": {
    "boolean_query": ""
  },
  "outreach_message": {
    "outreach_message": "",
    "specific_detail": "",
    "character_count": 0,
    "attempts": 0
  },
  "candidate_summary": {
    "name": "",
    "current_company": "",
    "key_skills": [],
    "fit_reason": "",
    "concerns": ""
  },
  "pipeline_trace": []
}
```

What NOT to do:
- Do not wrap required outputs inside an `outputs` object.
- Do not change required top-level key names.
- Do not emit only strings where objects are required.

---

## 8) Retry Loop Architecture for Step 4

Step 4 must explicitly show:

- `max_attempts = 3`
- For attempts 1..3:
  - Generate outreach message via LLM call.
  - Evaluate using a visible evaluation prompt in code (or prompt file) and explicit deterministic checks:
    - under 300 chars
    - includes a specific JD detail
    - personalized startup-oriented tone, avoiding generic AI-sounding language
  - If valid:
    - accept message
    - append success trace entry
    - exit loop
  - If invalid:
    - append retry trace entry with reason in `note`
    - re-prompt model with correction instruction
- After attempt 3 still invalid:
  - gracefully fail
  - set `outreach_message` object fields with explicit failure-safe values
  - append final failure trace entry

Graceful failure policy (recommended):
- Interpret “exit gracefully” as exiting the Step 4 retry loop without crashing the run; keep pipeline running to Step 5 so the full 5-step workflow remains intact.
- Step 5 notes outreach validity status in summary context.

---

## 9) Error Handling Strategy

- Input validation at startup:
  - JD must exist and be non-empty.
  - Manager notes may be empty/missing.
- Step-level try/except in orchestrator:
  - record trace event on failure using required trace fields
  - continue only when reasonable; otherwise end with controlled output
- Always produce `output.json`, even on partial failure.

Failure output behavior:
- Required top-level keys still present.
- Missing/failed values should still keep required object structure with safe defaults + explanatory trace note.

---

## 10) Prompt Organization Strategy

- One prompt file per step for clarity and easy review.
- Prompts should enforce concise structured outputs.
- Step 4 prompt supports correction context:
  - previous invalid message
  - failure reason
  - constraints reminder

Why:
- Makes “multi-step agent pipeline” visible in both code and prompts.
- Simplifies iteration without changing orchestration logic.

---

## 11) Recommended Libraries

Minimal set:
- `openai` (or target LLM SDK)
- `python-dotenv` (optional env loading)
- stdlib: `json`, `dataclasses`, `typing`, `pathlib`, `time`, `datetime`

Optional:
- `pydantic` if you want stricter schema parsing.

Avoid:
- Heavy agent frameworks for this assignment unless strictly necessary.

---

## 12) FastAPI / CLI / Frontend Recommendation

Recommendation:
- Use CLI script only (`python main.py`) for core assignment.

Why:
- Directly satisfies run requirement.
- Reduces complexity and review overhead.

Optional:
- Add lightweight visualization as a separate helper script only.

---

## 13) Recommended Implementation Order

1. Define input/output contracts and strict schema mappings.
2. Implement `PipelineState` + trace helper.
3. Implement orchestrator skeleton with 5 explicit step calls.
4. Implement Steps 1–3.
5. Implement Step 4 retry + validator.
6. Implement Step 5 summary (with internal mock candidate snippets if needed).
7. Implement `output.json` serialization with strict top-level keys.
8. Run end-to-end sanity test.

---

## 14) Potential Edge Cases

- JD text too short or ambiguous.
- Optional manager notes absent.
- LLM output too verbose or malformed.
- Step 4 repeatedly violates constraints.
- JD lacks concrete details, making “specific detail” extraction harder.
- API transient errors/timeouts.

Mitigation:
- deterministic parsing rules
- explicit fallback messages
- trace notes with reasoned outcomes

---

## 15) Most Important Parts for Evaluation

- Exactly 5 distinct sequential LLM calls.
- Clear step boundaries and chaining.
- Step 4 visible self-correction retry loop with max 3 attempts.
- Assignment-compatible `pipeline_trace` keys.
- Assignment-compatible `output.json` top-level keys.
- Runnable with `python main.py`.
- README includes clean-machine setup, pinned dependencies, and a Sample Run with full terminal output + generated `output.json`.

---

## 16) What Makes It Look Production-Like

- Clean module boundaries.
- Explicit contracts and deterministic output shape.
- Reliable retry + validation behavior.
- Traceability for every meaningful step action.
- Graceful degradation instead of crashing.

Production-like here means robust and readable, not over-abstracted.

---

## 17) Suggestions for Lightweight UI Visualization (Optional)

Keep optional and small:
- `view_trace.py` reads `output.json` and prints a timeline table.
- Optional single HTML file to visualize:
  - final outputs
  - pipeline trace entries
  - Step 4 attempts and outcomes

No impact on core required deliverable.

---

## 18) Recommended Development Phases

- Phase 1: Contract-first skeleton (state, trace, output schema).
- Phase 2: Implement 5-step happy path.
- Phase 3: Harden Step 4 retry/validation and graceful fail behavior.
- Phase 4: Strengthen error handling and edge-case behavior.
- Phase 5: Final polish (README, sample input, demonstration output).

---

## 19) README and Write-Up Requirements (Must Include)

- Reproducible setup instructions for a clean machine.
- Pinned dependencies in `requirements.txt`.
- One real Sample Run section with:
  - full terminal output
  - full generated `output.json`
- Brief answers to required reflection questions:
  - What would you improve with another week?
  - What was implicit/unstated but important in the task?
  - Why 5-step pipeline instead of 1-step? What breaks if Steps 1 and 2 are collapsed?
  - Which parts used AI assistance vs your own judgment?

---

## Reviewer-Focused Compliance Checklist

- [ ] Input uses only JD + optional manager notes.
- [ ] 5 steps are separate and sequential.
- [ ] Step 4 has explicit visible retry loop (max 3).
- [ ] `pipeline_trace` uses `step` as integer (1..5) and `result` in `pass/retry/fail`.
- [ ] `pipeline_trace` entries contain required keys: `step/action/attempt/result/note`.
- [ ] `output.json` top-level keys and nested field structure match assignment exactly.
- [ ] Runs locally with `python main.py`.
- [ ] `requirements.txt` uses pinned versions.
- [ ] README includes reproducible setup + full Sample Run terminal output + `output.json`.
- [ ] README includes the required brief write-up answers.

---

## B. 中文版本（完整对应版）

## 1）推荐项目架构（Recommended Project Architecture）
采用清晰的模块化串行流水线架构：一个编排器（orchestrator）+ 五个明确分离的步骤模块。

- 入口固定为 `python main.py`。
- `main.py` 只负责读取作业输入（Job Description 必填、Hiring Manager Notes 选填）、顺序执行 5 个步骤、写出 `output.json`。
- 每个步骤独立文件/函数，且每步都有可见的单次 LLM 调用（Step 4 除外：允许重试调用）。
- Step 4 必须在代码中显式实现“校验 + 重试循环（最多 3 次）”。
- 通过 `PipelineState（流水线状态对象）` 在步骤间传递中间结果。

设计理由：
- 评审可以一眼验证“多步、串行、可追踪、合规”。
- 保持工程可读性，不引入不必要复杂度。

不要这样做：
- 不要把 5 步合并成一个大 Prompt。
- 不要把重试逻辑藏在难以审查的通用中间件里。
- 不要为了“看起来高级”引入重型框架。

---

## 2）目录结构（Folder Structure）

```text
AI_Recruiting_Agent/
  main.py
  requirements.txt
  README.md
  output.json

  app/
    orchestrator.py
    state.py
    llm_client.py

    steps/
      step1_extract_jd_signals.py
      step2_generate_search_strategy.py
      step3_generate_boolean_query.py
      step4_generate_outreach_message.py
      step5_generate_candidate_summary.py

    prompts/
      step1_prompt.txt
      step2_prompt.txt
      step3_prompt.txt
      step4_prompt.txt
      step5_prompt.txt

    validators/
      outreach_validator.py

    tracing/
      trace_utils.py

  data/
    input.json
```

理由：
- 结构精简但完整。
- 步骤边界非常清晰，便于评审。
- Prompt 与校验器独立，便于调试与迭代。

---

## 3）文件职责（File-by-File Responsibilities）

- `main.py`：读取输入、初始化 `PipelineState`、调用编排器、输出 `output.json`。
- `app/orchestrator.py`：按 1→5 严格顺序执行，统一异常边界。
- `app/state.py`：定义 `PipelineState`（输入、中间结果、最终结果、trace）。
- `app/llm_client.py`：LLM 调用薄封装，不承载业务逻辑。
- `app/steps/step1_extract_jd_signals.py`：Step 1 的 Prompt 与解析逻辑。
- `app/steps/step2_generate_search_strategy.py`：Step 2 的 Prompt 与解析逻辑。
- `app/steps/step3_generate_boolean_query.py`：Step 3 的 Prompt 与解析逻辑。
- `app/steps/step4_generate_outreach_message.py`：Step 4 生成、显式校验、重试循环。
- `app/steps/step5_generate_candidate_summary.py`：Step 5 总结生成（如需候选人样本，使用流水线内部 mock 数据）。
- `app/prompts/*.txt`：每步一个 Prompt 模板。
- `app/validators/outreach_validator.py`：校验长度与 JD 细节命中。
- `app/tracing/trace_utils.py`：按作业要求写入 trace 条目。

---

## 4）步骤间数据流（Data Flow Between Pipeline Steps）

严格输入规则：
- 作业外部输入仅有：
  - Job Description（必填）
  - Hiring Manager Notes（选填）
- 不存在外部 `candidate profile` 输入。

串行流程：
1. `extract_jd_signals`
   - 输入：JD + 可选 manager notes
   - 输出：结构化岗位信号（角色类型、必备技能、资深度信号、公司阶段、缺失信息标记）
2. `generate_search_strategy`
   - 输入：Step 1 输出
   - 输出：候选人搜索策略
3. `generate_boolean_query`
   - 输入：Step 1 + Step 2 输出
   - 输出：Boolean 检索语句
4. `generate_outreach_message`
   - 输入：Step 1 + Step 2 + Step 3 输出
   - 输出：外联消息（带重试校验；语气需个性化、偏创业公司风格、避免泛化 AI 文风）
5. `generate_candidate_summary`
   - 输入：Step 1–4 输出 + 内部生成的 mock candidate snippets（如需要）
   - 输出：候选人总结

Step 5 说明：
- 如业务语义需要“候选人信息片段”，应由流水线内部生成（或在 Step 5 内生成），不能作为外部输入假设。

---

## 5）状态管理策略（State Management Strategy）

使用单一 `PipelineState（流水线状态对象）`：

- `job_description`
- `hiring_manager_notes`（可选）
- `jd_signals`
- `candidate_search_strategy`
- `boolean_query`
- `outreach_message`
- `candidate_summary`
- `pipeline_trace`（trace 列表）
- `internal_context`（临时上下文，含 Step 5 可能使用的内部 mock 数据）

理由：
- 数据责任清晰。
- 调试简单。
- 评审可快速验证步骤串联关系。

---

## 6）`pipeline_trace` 设计（严格对齐作业字段）

每条 trace 必须保留作业要求字段（名称不改）：

- `step`（整数：1..5）
- `action`
- `attempt`
- `result`
- `note`

字段取值规则（按作业原文）：
- `step`：必须是步骤编号整数，不能写字符串
- `action`：必须是固定步骤名之一：
  - `extract_jd_signals`
  - `generate_search_strategy`
  - `generate_boolean_query`
  - `generate_outreach_message`
  - `generate_candidate_summary`
- `result`：仅允许 `pass` / `retry` / `fail`
- Step 4 必须记录每一次尝试（attempt 1/2/3）

提交安全建议：
- `pipeline_trace` 默认只保留作业要求的必需字段。
- 时间戳/耗时/模型名/校验细节等额外观测信息，建议写入独立内部调试日志文件。

如果你确实要在 trace 中放额外信息，必须放到可选嵌套字段 `metadata` 下。示例：

```json
{
  "step": 4,
  "action": "generate_outreach_message",
  "attempt": 2,
  "result": "retry",
  "note": "Failed validation: exceeded 300 characters",
  "metadata": {
    "duration_ms": 412,
    "validation": {
      "length_ok": false,
      "has_jd_detail": true
    }
  }
}
```

不要这样做：
- 不要自创替换字段名（如 `status` 替代 `result`）。
- 不要把 metadata 字段平铺到顶层破坏契约。
- 不要让可选 metadata 影响评测器对必需字段的解析。

---

## 7）`output.json` 设计（严格顶层对齐）

顶层必须包含且仅对齐这些必需键：

- `candidate_search_strategy`
- `boolean_query`
- `outreach_message`
- `candidate_summary`
- `pipeline_trace`

为确保评审兼容性，提交版本不增加额外顶层键。

同时必须满足字段级结构要求：

1. `candidate_search_strategy`（对象）
- `target_backgrounds`: list[string]
- `target_companies`: list[string]
- `keywords`: list[string]
- `seniority`: string

2. `boolean_query`（对象）
- `boolean_query`: string

3. `outreach_message`（对象）
- `outreach_message`: string（严格 < 300 字符）
- `specific_detail`: string（用于个性化的 JD 原文短语）
- `character_count`: integer
- `attempts`: integer

4. `candidate_summary`（对象）
- `name`: string（允许 mock）
- `current_company`: string
- `key_skills`: list[string]（3 到 5 个）
- `fit_reason`: string
- `concerns`: string

5. `pipeline_trace`（list[object]）
- 每条记录都必须包含 `step/action/attempt/result/note`

推荐结构：

```json
{
  "candidate_search_strategy": {
    "target_backgrounds": [],
    "target_companies": [],
    "keywords": [],
    "seniority": ""
  },
  "boolean_query": {
    "boolean_query": ""
  },
  "outreach_message": {
    "outreach_message": "",
    "specific_detail": "",
    "character_count": 0,
    "attempts": 0
  },
  "candidate_summary": {
    "name": "",
    "current_company": "",
    "key_skills": [],
    "fit_reason": "",
    "concerns": ""
  },
  "pipeline_trace": []
}
```

不要这样做：
- 不要再包一层 `outputs`。
- 不要改动必需顶层 key 名称。
- 不要把需要对象的字段错误写成纯字符串。

---

## 8）Step 4 重试循环架构（Retry Loop Architecture for Step 4）

Step 4 必须显式实现：

- `max_attempts = 3`
- 对 `attempt = 1..3`：
  - 调用 LLM 生成 outreach 文案
  - 在代码（或独立 Prompt 文件）中保留可见的 evaluation prompt，并结合显式规则校验：
    - 字符数 `< 300`
    - 包含至少一个“具体 JD 细节”
    - 语气符合个性化创业招聘风格，避免模板化 AI 文风
  - 若通过：
    - 接受结果
    - 写入成功 trace
    - 退出循环
  - 若失败：
    - 在 `note` 写明失败原因并记录 retry trace
    - 带纠错提示再次请求 LLM
- 若 3 次仍失败：
  - 优雅失败（graceful fail）
  - `outreach_message` 对象仍保持完整字段结构，并填入失败兜底值
  - 记录最终失败 trace

推荐策略：
- 将“graceful exit”解释为：Step 4 重试循环有序退出且程序不崩溃；同时继续执行 Step 5，保持完整 5 步流水线，并在 summary 上下文标注外联状态。

---

## 9）错误处理策略（Error Handling Strategy）

- 启动阶段输入校验：
  - JD 必须非空
  - manager notes 可空
- 编排器进行步骤级 try/except：
  - 出错即写 trace（使用规定字段）
  - 判断是否继续或终止，但始终可控
- 无论成功或失败，都要生成 `output.json`。

失败输出约定：
- 必需顶层键必须存在。
- 即使失败也要维持必需对象字段完整，并通过 trace 的 `note` 说明原因。

---

## 10）Prompt 组织策略（Prompt Organization Strategy）

- 每一步一个独立 Prompt 文件，方便审查。
- Prompt 输出要求尽量结构化、简洁、可解析。
- Step 4 Prompt 支持注入纠错上下文：
  - 上次失败文案
  - 失败原因
  - 约束提醒

理由：
- “多步 Agent 管道”在代码与 Prompt 层都清晰可见。

---

## 11）推荐库（Recommended Libraries）

最小可行集合：
- `openai`（或目标 LLM SDK）
- `python-dotenv`（可选）
- 标准库：`json`、`dataclasses`、`typing`、`pathlib`、`time`、`datetime`

可选增强：
- `pydantic`（严格结构校验时使用）

避免：
- 非必要的重型 Agent 框架。

---

## 12）是否使用 FastAPI / CLI / 前端

建议：
- 核心交付只用 CLI 脚本：`python main.py`。

原因：
- 直接满足作业运行要求。
- 降低复杂度，利于评审。

可选：
- 额外做轻量可视化脚本，但不要影响核心交付结构。

---

## 13）推荐实现顺序（Recommended Implementation Order）

1. 先定义输入输出契约与严格 schema 映射。
2. 实现 `PipelineState` 与 trace 工具。
3. 搭建 orchestrator 骨架，明确 5 步顺序调用。
4. 实现 Step 1–3。
5. 实现 Step 4 重试 + 校验器。
6. 实现 Step 5（如需候选人片段，使用内部 mock 生成）。
7. 实现 `output.json` 严格序列化（顶层 key 对齐）。
8. 进行端到端联调与 sanity check。

---

## 14）潜在边界场景（Potential Edge Cases）

- JD 内容过短/过模糊。
- manager notes 缺失（正常可选）。
- LLM 输出格式异常或过长。
- Step 4 连续 3 次不满足约束。
- JD 缺少可引用“具体细节”导致校验困难。
- API 超时或瞬时错误。

缓解方式：
- 明确解析规则
- 明确兜底文案
- trace 中记录可审计的失败原因

---

## 15）评估最关键点（Most Important for Evaluation）

- 5 个明确、串行、彼此衔接的 LLM 调用步骤。
- Step 4 具备“可见的”自纠错重试逻辑（最多 3 次）。
- `pipeline_trace` 字段严格合规（`step/action/attempt/result/note`）。
- `output.json` 顶层键严格合规。
- 本地可直接运行 `python main.py`。
- README 包含可复现实验环境、依赖固定版本、完整 Sample Run 终端输出与真实 `output.json`。

---

## 16）如何体现生产感（Production-Like Quality）

- 模块职责清晰，结构稳定。
- 输出结构确定性强，可重复审查。
- 重试和校验行为可靠可解释。
- 失败可回溯、可降级，而不是崩溃退出。

这里的“生产感”强调可靠与可读，不是堆叠抽象层。

---

## 17）轻量可视化建议（可选）

保持可选、轻量：
- `view_trace.py`：读取 `output.json`，终端打印步骤时间线。
- 可选单页 HTML：展示最终输出 + trace + Step 4 尝试记录。

不影响核心必需交付。

---

## 18）推荐开发阶段（Recommended Development Phases）

- Phase 1：契约优先（state、trace、output schema）。
- Phase 2：先跑通 5 步 happy path。
- Phase 3：强化 Step 4 重试与优雅失败。
- Phase 4：补齐异常处理与边界场景。
- Phase 5：README、示例输入、示例输出打磨。

---

## 19）README 与简短说明（必须包含）

- 可在 clean machine 复现的安装与运行说明。
- `requirements.txt` 依赖固定版本（pinned）。
- 一次真实 Sample Run，包含：
  - 完整终端输出
  - 完整生成的 `output.json`
- 对必答反思问题给出简短回答：
  - 如果再给一周会改进什么？
  - 这个任务有哪些“没明说但关键”的点？
  - 为什么设计成 5 步而不是 1 步？若合并 Step 1 和 Step 2 会破坏什么？
  - 哪些部分用了 AI，哪些部分依赖你自己的判断？

---

## 评审向合规检查清单（Reviewer Checklist）

- [ ] 输入仅使用 JD + 可选 manager notes。
- [ ] 5 个步骤独立且串行。
- [ ] Step 4 显式重试循环，最多 3 次。
- [ ] `pipeline_trace.step` 为整数（1..5），`result` 仅为 `pass/retry/fail`。
- [ ] `pipeline_trace` 含必需字段：`step/action/attempt/result/note`。
- [ ] `output.json` 顶层键与内部字段结构均与作业要求完全一致。
- [ ] 可通过 `python main.py` 本地运行。
- [ ] `requirements.txt` 采用固定版本（pinned versions）。
- [ ] README 含 clean machine setup + 完整 Sample Run 终端输出 + `output.json`。
- [ ] README 含必答的简短 write-up 问题回答。
