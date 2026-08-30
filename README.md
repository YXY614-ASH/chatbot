# AI 学习助手（Chatbot）

一个能多轮对话的网页聊天机器人，背后是 **DeepSeek** 大模型。

这是吴佳诣学习「AI 应用开发」的第一个项目：从一个 52 行的单文件 MVP 开始，逐步重构为分层结构。

## 版本历史

| 版本 | 说明 | 入口文件 | 查看方式 |
|------|------|----------|----------|
| **V0.1** | 单文件 MVP，功能跑通 | `ai_assistant.py` | `git checkout V0.1` |
| **V0.2** | 工程化重构（分层 + 流式输出 + 命令行参数） | `main.py` | 当前 `main` 分支 |

## V0.1 → V0.2 重构了什么

1. **配置分离**：`config.py` 集中管理 key、模型、语气等参数，改配置不用翻业务代码。
2. **代码分层**：`client.py`（模型调用）与 `main.py`（界面）职责分离。
3. **流式输出**：回答像打字机一样逐字显示，不再干等整段。
4. **错误处理**：网络异常、额度不足等会给出友好提示，而不是直接崩溃。
5. **命令行参数**：`--port` / `--share` / `--server-name` 灵活启动。

## V0.2 目录结构

```
chatbot/
├── README.md          # 本说明
├── requirements.txt   # 依赖清单
├── .gitignore         # 忽略缓存等文件
├── config.py          # 配置：key、模型、语气、界面文案
├── client.py          # DeepSeek 客户端 + 流式对话函数
├── main.py            # 入口：Gradio 界面 + 命令行参数
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

## 技术栈

- Python 3.12
- [Gradio](https://www.gradio.app/) — 网页界面
- [OpenAI SDK](https://github.com/openai/openai-python) — 调用 DeepSeek（兼容 OpenAI 接口）

## ⚠️ 安全说明

`config.py` 里的 API key 已随公开仓库暴露，请勿继续用于敏感操作，建议到 [DeepSeek 开放平台](https://platform.deepseek.com) 吊销并重新生成。
