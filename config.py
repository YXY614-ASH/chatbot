# -*- coding: utf-8 -*-
"""
配置模块 —— 集中管理所有「会变的东西」。

为什么单独放一个文件？
    把配置和业务逻辑分开，以后想改 key、改模型、改回答语气，
    只需要动这一个文件，不用去翻业务代码。
"""

import prompt_templates


# ============ 1. API 密钥 ============
# ⚠️ 安全提醒：API key 等同于账户密码。
#    这个仓库是公开的，下面的 key 已经随代码一起公开了。
#    请不要继续用它做敏感操作，建议去 https://platform.deepseek.com
#    吊销并重新生成一个 key，再填回这里。
API_KEY = "sk-ada25e18f3ee46f7ab80eb786036d826"

# ============ 2. 模型与接口配置 ============
BASE_URL = "https://api.deepseek.com"  # DeepSeek 兼容 OpenAI 接口
MODEL = "deepseek-chat"                # 模型名

# ============ 3. 对话行为配置 ============
TEMPERATURE = 0.7                      # 0=严谨，1=发散；聊天用 0.7 合适
SYSTEM_PROMPT = "你是吴佳诣的学习助手，回答简洁、准确、用中文。"

DEFAULT_MODE = "PDF资料问答"
MODE_PRESETS = {
    "学习助手": {
        "temperature": 0.7,
        "system_prompt": SYSTEM_PROMPT,
        "description": "适合日常学习答疑、概念解释和学习规划。",
    },
    "PDF资料问答": {
        "temperature": 0.3,
        "system_prompt": """你是吴佳诣的 PDF 资料问答助手，回答要基于用户上传的 PDF 资料。
如果系统消息中提供了“PDF 资料片段”，优先依据这些片段回答，并在回答末尾列出参考页码。
如果资料片段不足以回答，要明确说明“PDF 中没有找到足够依据”，再给出你的合理建议。
如果用户没有上传 PDF，先提醒用户上传 PDF，再提供通用回答。""",
        "description": "适合上传课件、路线图或讲义后，围绕 PDF 内容提问。",
    },
    "题目解析卡": {
        "temperature": 0.2,
        "system_prompt": prompt_templates.QUESTION_ANALYSIS_CARD_PROMPT,
        "description": "适合贴题目后输出固定格式的分析卡。",
    },
    "学习计划卡": {
        "temperature": 0.4,
        "system_prompt": prompt_templates.STUDY_PLAN_CARD_PROMPT,
        "description": "适合输入学习目标后输出固定格式的计划卡。",
    },
}

# ============ 4. PDF / RAG 配置 ============
PDF_CHUNK_SIZE = 900                   # 每个片段的最大字符数
PDF_CHUNK_OVERLAP = 120                # 相邻片段重叠，避免切断上下文
PDF_TOP_K = 3                          # 每次提问取最相关的片段数量

# ============ 5. 界面配置 ============
APP_TITLE = "AI 学习助手"
APP_DESCRIPTION = "可上传 PDF 做资料问答，也可切换到题目解析卡或学习计划卡，按固定格式输出。"
