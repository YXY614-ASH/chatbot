# -*- coding: utf-8 -*-
"""
课程助手 Agent 模块。

V0.5 的 Agent 先做成清晰可验证的本地工具联动：
    1. 根据问题决定是否查 PDF
    2. 根据问题决定是否调用计算器
    3. 把工具结果整理给大模型生成最终回答
"""

import ast
import operator
import re

import document


CALCULATOR_KEYWORDS = ("计算", "算", "等于", "多少", "+", "-", "*", "/", "×", "÷", "^")
PDF_KEYWORDS = ("pdf", "资料", "课件", "文档", "讲义", "路线图", "根据", "里面", "第")

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def plan_tools(question, pdf_file=None):
    """根据问题和输入决定需要哪些工具。"""
    question = question or ""
    tools = []

    if pdf_file and _contains_any(question, PDF_KEYWORDS):
        tools.append("pdf_search")

    if _looks_like_calculation(question):
        tools.append("calculator")

    if not tools and pdf_file:
        tools.append("pdf_search")

    return tools


def run_agent_tools(question, pdf_file=None):
    """执行工具计划，返回可拼入提示词的上下文和用户可见摘要。"""
    tools = plan_tools(question, pdf_file)
    results = []
    visible_lines = ["Agent 工具计划：" + ("、".join(_tool_label(tool) for tool in tools) if tools else "直接回答")]

    if "pdf_search" in tools:
        context, summary = document.build_pdf_context(pdf_file, question)
        visible_lines.append(f"- PDF资料检索：{summary}")
        if context:
            results.append("【PDF资料检索结果】\n" + context)

    if "calculator" in tools:
        calculation = calculate_from_text(question)
        visible_lines.append(f"- 计算器：{calculation['summary']}")
        if calculation["results"]:
            lines = [
                f"{item['expression']} = {item['value']}"
                for item in calculation["results"]
            ]
            results.append("【计算器结果】\n" + "\n".join(lines))

    return "\n\n".join(results), "\n".join(visible_lines)


def calculate_from_text(text):
    """从文本中提取安全算式并计算。"""
    expressions = extract_expressions(text)
    results = []
    errors = []

    for expression in expressions:
        try:
            value = safe_eval(expression)
            results.append({"expression": expression, "value": _format_number(value)})
        except Exception as exc:
            errors.append(f"{expression}: {exc}")

    if results:
        summary = "；".join(f"{item['expression']} = {item['value']}" for item in results)
    elif errors:
        summary = "找到算式但计算失败：" + "；".join(errors)
    else:
        summary = "没有识别到可直接计算的算式"

    return {"results": results, "errors": errors, "summary": summary}


def extract_expressions(text):
    """提取包含运算符的算式，避免把普通数字误当作题目。"""
    normalized = (
        (text or "")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("^", "**")
    )
    candidates = re.findall(r"(?<!\w)[\d\s+\-*/().]+(?:\*\*)?[\d\s+\-*/().]*(?!\w)", normalized)
    expressions = []
    for candidate in candidates:
        expression = re.sub(r"\s+", "", candidate).strip(".")
        if len(expression) < 3:
            continue
        if not re.search(r"\d[+\-*/]|\*\*", expression):
            continue
        if expression not in expressions:
            expressions.append(expression)
    return expressions


def safe_eval(expression):
    """只允许数字和基础四则运算，避免执行任意代码。"""
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError("只支持数字、括号和基础四则运算")


def _looks_like_calculation(question):
    return _contains_any(question, CALCULATOR_KEYWORDS) and bool(extract_expressions(question))


def _contains_any(text, keywords):
    lowered = (text or "").lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _tool_label(tool):
    labels = {
        "pdf_search": "PDF资料检索",
        "calculator": "计算器",
    }
    return labels.get(tool, tool)


def _format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(round(value, 10))
