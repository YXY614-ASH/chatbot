# -*- coding: utf-8 -*-
"""
模型客户端模块 —— 封装 DeepSeek 的调用，对外只暴露一个 chat_stream 函数。

界面层（main.py）只需要调 chat_stream，不需要关心 OpenAI SDK 的细节。
这就是「分层」的好处：每层只管自己那一摊事。
"""

from openai import OpenAI

import config
import document

# 创建客户端（模块加载时执行一次，复用连接，不用每次提问都重建）
_client = OpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL,
)


def get_mode_names():
    """返回界面可选的对话模式名称。"""
    return list(config.MODE_PRESETS.keys())


def get_mode_description(mode):
    """返回当前模式的简短说明，用于界面提示。"""
    preset = _get_mode_preset(mode)
    return preset["description"]


def _get_mode_preset(mode):
    """找不到模式时回退到默认模式，避免界面传空值导致报错。"""
    return config.MODE_PRESETS.get(mode) or config.MODE_PRESETS[config.DEFAULT_MODE]


def _append_history_messages(messages, history):
    """兼容 Gradio tuple history 和 messages history 两种格式。"""
    for item in history or []:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
            continue

        if isinstance(item, (list, tuple)) and len(item) >= 2:
            user_msg, bot_msg = item[0], item[1]
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if bot_msg:
                messages.append({"role": "assistant", "content": bot_msg})


def _build_messages(message, history, mode=None, pdf_context=None):
    """把界面传来的「本次提问 + 历史对话」拼成模型要的 messages 格式。"""
    preset = _get_mode_preset(mode)
    system_prompt = preset["system_prompt"]
    if pdf_context:
        system_prompt = f"{system_prompt}\n\nPDF 资料片段：\n{pdf_context}"

    messages = [{"role": "system", "content": system_prompt}]
    _append_history_messages(messages, history)
    messages.append({"role": "user", "content": message})
    return messages


def chat_stream(message, history, mode=None, pdf_file=None):
    """流式对话：逐段返回模型回答，实现「打字机」效果。

    这是一个生成器（generator），用 yield 把一段段文本吐给界面，
    界面会边生成边显示，不用等整段答案算完。
    """
    preset = _get_mode_preset(mode)
    pdf_context = None
    answer = ""

    if mode == "PDF资料问答" and pdf_file:
        try:
            pdf_context, pdf_summary = document.build_pdf_context(pdf_file, message)
            answer = f"{pdf_summary}\n\n"
            yield answer
        except Exception as exc:
            yield f"⚠️ PDF 读取失败：{exc}"
            return

    messages = _build_messages(message, history, mode, pdf_context)
    try:
        stream = _client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            temperature=preset["temperature"],
            stream=True,  # 开启流式返回
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                answer += delta.content
                yield answer
    except Exception as exc:  # 捕获网络/额度/鉴权等异常，给用户友好提示
        yield f"{answer}\n\n⚠️ 出错了：{exc}"
