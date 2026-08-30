# -*- coding: utf-8 -*-
"""
程序入口 —— 负责界面展示和命令行参数，具体模型调用交给 client 模块。

运行：
    python main.py                  # 本机访问 http://127.0.0.1:7860
    python main.py --port 8000      # 换端口
    python main.py --share          # 生成一个临时公网链接
"""

import argparse

import gradio as gr

import client
import config


def parse_args():
    """解析命令行参数，让启动方式更灵活。"""
    parser = argparse.ArgumentParser(description="AI 学习助手")
    parser.add_argument("--server-name", default="127.0.0.1", help="监听地址，局域网用 0.0.0.0")
    parser.add_argument("--port", type=int, default=7860, help="端口")
    parser.add_argument("--share", action="store_true", help="生成公网临时链接")
    return parser.parse_args()


def main():
    args = parse_args()
    mode_selector = gr.Dropdown(
        choices=client.get_mode_names(),
        value=config.DEFAULT_MODE,
        label="模式",
        info=client.get_mode_description(config.DEFAULT_MODE),
    )
    gr.ChatInterface(
        fn=client.chat_stream,        # 传生成器函数 → 自动流式显示
        title=config.APP_TITLE,
        description=config.APP_DESCRIPTION,
        additional_inputs=[mode_selector],
    ).launch(
        server_name=args.server_name,
        server_port=args.port,
        share=args.share,
    )


if __name__ == "__main__":
    main()
