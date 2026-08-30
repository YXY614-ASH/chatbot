# -*- coding: utf-8 -*-
"""
模型客户端模块 —— 封装 DeepSeek 的调用，对外只暴露一个 chat_stream 函数。

界面层（main.py）只需要调 chat_stream，不需要关心 OpenAI SDK 的细节。
这就是「分层」的好处：每层只管自己那一摊事。
"""

from openai import OpenAI

import config

# 创建客户端（模块加载时执行一次，复用连接，不用每次提问都重建）
_client = OpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL,
)


def _build_messages(message, history):
    """把界面传来的「本次提问 + 历史对话」拼成模型要的 messages 格式。"""
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})
    return messages


def chat_stream(message, history):
    """流式对话：逐段返回模型回答，实现「打字机」效果。

    这是一个生成器（generator），用 yield 把一段段文本吐给界面，
    界面会边生成边显示，不用等整段答案算完。
    """
    messages = _build_messages(message, history)
    try:
        stream = _client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            temperature=config.TEMPERATURE,
            stream=True,  # 开启流式返回
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
    except Exception as exc:  # 捕获网络/额度/鉴权等异常，给用户友好提示
        yield f"\n\n⚠️ 出错了：{exc}"
