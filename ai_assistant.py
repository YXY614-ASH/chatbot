# -*- coding: utf-8 -*-
"""
AI 学习助手 —— 你的第一个 LLM 应用（MVP）
功能：一个能多轮对话的网页聊天机器人，背后是 DeepSeek 大模型
"""

import os
from openai import OpenAI
import gradio as gr

# ============ 1. 配置 API key ============
# 已经按「方式B」帮你把 key 直接写在这里了。
# 注意：这个文件里有你的 key，别发给别人、别传到公开的 git 仓库。
API_KEY = "sk-ada25e18f3ee46f7ab80eb786036d826"

if not API_KEY:
    print("=" * 50)
    print("还没配置 API key！")
    print("1. 去 https://platform.deepseek.com 注册并创建 key")
    print("2. 把 key 填到本文件 API_KEY 那一行，或设置环境变量 DEEPSEEK_API_KEY")
    print("=" * 50)
    raise SystemExit(1)

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",  # DeepSeek 兼容 OpenAI 接口
)

# ============ 2. 对话函数（核心） ============
# ChatInterface 会自动把「历史对话」传给 history，我们只需把它转成模型要的格式
def chat(message, history):
    # 拼出给模型的完整消息列表：系统设定 + 历史对话 + 本次提问
    messages = [{"role": "system", "content": "你是吴佳诣的学习助手，回答简洁、准确、用中文。"}]
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    # 调用大模型
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7,  # 0=严谨，1=发散；聊天用 0.7 合适
    )
    return resp.choices[0].message.content

# ============ 3. 启动网页界面 ============
gr.ChatInterface(
    fn=chat,
    title="AI 学习助手",
    description="试试问我：「用通俗的话解释什么是过拟合」或「帮我规划三极管的学习」",
).launch()
