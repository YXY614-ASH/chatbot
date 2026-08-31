# AI 学习助手（Chatbot）

一个能多轮对话的网页聊天机器人，背后是 **DeepSeek** 大模型。

这是吴佳诣学习「AI 应用开发」的第一个项目：从一个 52 行的单文件 MVP 开始，逐步迭代成能查资料、会用工具、可交付的课程助手。

## 版本历史

| 版本 | 说明 | 入口文件 | 查看方式 |
|------|------|----------|----------|
| **V0.1** | 单文件 MVP，功能跑通 | `ai_assistant.py` | `git checkout V0.1` |
| **V0.2** | 工程化重构（分层 + 流式输出 + 命令行参数） | `main.py` | `git checkout V0.2` |
| **V0.3** | PDF 资料问答：上传 PDF → 提取文本 → 检索片段 → 结合 DeepSeek 回答 | `main.py` | `git checkout V0.3` |
| **V0.4** | 提示工程升级：题目解析卡 + 学习计划卡固定格式输出 | `main.py` | 当前 `main` 分支 |

## 小版本路线图

| 版本 | 对应阶段 | 目标 | 验证标准 |
|------|----------|------|----------|
| **V0.1** | ② LLM 调用 | 跑通 DeepSeek 网页聊天机器人 MVP | 能打开网页并完成单轮问答 |
| **V0.2** | ② LLM 调用 | 完成工程化重构 | 配置、模型调用、界面入口分层；支持流式输出和命令行参数 |
| **V0.3** | ④ RAG | 上传 PDF 后基于资料回答 | 能读取 PDF、检索相关片段，并在回答中说明来源页码 |
| **V0.4** | ③ 提示工程 | 加强结构化输出和模板化提示词 | 能按固定格式输出题目解析卡、学习计划卡 |
| **V0.5** | ⑤ Agent | 做会办事的课程助手 | 能按问题自动选择查资料、算题等工具 |
| **V0.6** | ⑥ 产品化 | 从 demo 走向可交付服务 | API key 改为环境变量，补日志、限流、部署说明 |

## V0.1 → V0.2 重构了什么

1. **配置分离**：`config.py` 集中管理 key、模型、语气等参数，改配置不用翻业务代码。
2. **代码分层**：`client.py`（模型调用）与 `main.py`（界面）职责分离。
3. **流式输出**：回答像打字机一样逐字显示，不再干等整段。
4. **错误处理**：网络异常、额度不足等会给出友好提示，而不是直接崩溃。
5. **命令行参数**：`--port` / `--share` / `--server-name` 灵活启动。

## V0.2 → V0.3 新增了什么

1. **PDF 上传入口**：Gradio 页面新增 PDF 文件上传控件。
2. **PDF 文本提取**：新增 `document.py`，使用 `pypdf` 读取 PDF 每页文字。
3. **资料切块检索**：把 PDF 内容切成小片段，并按用户问题检索最相关内容。
4. **带资料回答**：`client.py` 会把检索到的 PDF 片段拼进提示词，让 DeepSeek 基于资料回答。
5. **来源页码**：资料片段包含页码，方便回答时说明依据来自哪一页。
6. **轻量测试**：新增 `tests/test_client.py`，验证消息组装、历史记录兼容和资料检索。

## V0.3 → V0.4 新增了什么

1. **提示模板分层**：新增 `prompt_templates.py`，集中管理固定格式提示词。
2. **题目解析卡**：新增「题目解析卡」模式，按题目类型、已知条件、解题思路、关键公式、最终答案、易错点、置信度输出。
3. **学习计划卡**：新增「学习计划卡」模式，按学习目标、基础判断、阶段安排、每周行动、练习项目、风险提醒、下一步输出。
4. **模板模式低温度**：结构化模板使用更低 temperature，让输出格式更稳定。
5. **测试覆盖**：新增模板模式测试，验证模式存在、模板标题固定、调用温度正确。

## V0.4 目录结构

```
chatbot/
├── README.md          # 本说明
├── requirements.txt   # 依赖清单
├── .gitignore         # 忽略缓存等文件
├── config.py          # 配置：key、模型、语气、PDF 检索参数、界面文案
├── prompt_templates.py # 固定格式提示词模板
├── document.py        # PDF 读取、切块和检索
├── client.py          # DeepSeek 客户端 + 流式对话函数
├── main.py            # 入口：Gradio 界面 + 命令行参数
├── tests/             # 自动化测试
└── 学习助手代码讲解.md  # V0.1 旧版代码讲解（历史文档）
```

## 安装依赖

```bash
python -m pip install --user -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 运行

```bash
python main.py              # 本机访问 http://127.0.0.1:7860
python main.py --port 8000  # 换端口
python main.py --share      # 生成临时公网链接
```

进入页面后：

1. 做资料问答：选择「PDF资料问答」，在「PDF 资料」处上传课件、讲义或路线图 PDF，再提问。
2. 做题目解析：选择「题目解析卡」，贴入题目。
3. 做学习规划：选择「学习计划卡」，输入学习目标和时间限制。

## 测试

```bash
python -m unittest discover -s tests
python -m py_compile config.py prompt_templates.py document.py client.py main.py tests/test_client.py
```

## 技术栈

- Python 3.12
- [Gradio](https://www.gradio.app/) — 网页界面
- [OpenAI SDK](https://github.com/openai/openai-python) — 调用 DeepSeek（兼容 OpenAI 接口）
- [pypdf](https://pypdf.readthedocs.io/) — 提取 PDF 文本

## ⚠️ 安全说明

`config.py` 里的 API key 已随公开仓库暴露，请勿继续用于敏感操作，建议到 [DeepSeek 开放平台](https://platform.deepseek.com) 吊销并重新生成。
