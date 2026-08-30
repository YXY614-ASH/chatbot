# -*- coding: utf-8 -*-
"""
PDF 文档处理模块。

负责三件事：
    1. 读取 PDF 文本
    2. 把长文本切成适合放进提示词的小片段
    3. 根据用户问题检索最相关的片段
"""

from collections import Counter
from pathlib import Path
import math
import re

from pypdf import PdfReader

import config


def resolve_file_path(file_obj):
    """兼容 Gradio 可能传入的 str、dict 或 FileData 对象。"""
    if not file_obj:
        return None
    if isinstance(file_obj, (str, Path)):
        return str(file_obj)
    if isinstance(file_obj, dict):
        return file_obj.get("path") or file_obj.get("name")
    return getattr(file_obj, "path", None) or getattr(file_obj, "name", None)


def extract_pdf_pages(file_obj):
    """提取 PDF 每一页的文本，返回 [{page, text}, ...]。"""
    file_path = resolve_file_path(file_obj)
    if not file_path:
        return []

    reader = PdfReader(file_path)
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = _normalize_text(page.extract_text() or "")
        if text:
            pages.append({"page": index, "text": text})
    return pages


def build_chunks(pages):
    """把每页文本切成带页码的小片段。"""
    chunks = []
    for page in pages:
        text = page["text"]
        start = 0
        while start < len(text):
            end = start + config.PDF_CHUNK_SIZE
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({"page": page["page"], "text": chunk_text})
            start += config.PDF_CHUNK_SIZE - config.PDF_CHUNK_OVERLAP
    return chunks


def retrieve_relevant_chunks(question, chunks, top_k=None):
    """用轻量 TF-IDF 风格打分，找出和问题最相关的片段。"""
    if not question or not chunks:
        return []

    top_k = top_k or config.PDF_TOP_K
    query_terms = _tokenize(question)
    if not query_terms:
        return chunks[:top_k]

    chunk_terms = [_tokenize(chunk["text"]) for chunk in chunks]
    doc_freq = Counter()
    for terms in chunk_terms:
        doc_freq.update(set(terms))

    scored = []
    total_docs = len(chunks)
    query_counts = Counter(query_terms)
    for chunk, terms in zip(chunks, chunk_terms):
        term_counts = Counter(terms)
        score = 0.0
        for term, query_count in query_counts.items():
            if term not in term_counts:
                continue
            idf = math.log((1 + total_docs) / (1 + doc_freq[term])) + 1
            score += query_count * term_counts[term] * idf
        if score:
            scored.append((score, chunk))

    if not scored:
        return chunks[:top_k]

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def build_pdf_context(file_obj, question):
    """根据上传的 PDF 和问题，生成可拼进 system prompt 的资料上下文。"""
    pages = extract_pdf_pages(file_obj)
    if not pages:
        return "", "没有从 PDF 中提取到文字。扫描件图片 PDF 需要 OCR，当前版本暂不支持。"

    chunks = build_chunks(pages)
    relevant_chunks = retrieve_relevant_chunks(question, chunks)
    if not relevant_chunks:
        return "", "PDF 已读取，但没有找到可用片段。"

    sections = []
    for index, chunk in enumerate(relevant_chunks, start=1):
        sections.append(f"[片段 {index} | 第 {chunk['page']} 页]\n{chunk['text']}")
    context = "\n\n".join(sections)
    summary = f"已读取 PDF：{len(pages)} 页，检索到 {len(relevant_chunks)} 个相关片段。"
    return context, summary


def _normalize_text(text):
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text):
    """中文免分词：中文按 2 字符片段，英文数字按词。"""
    text = text.lower()
    words = re.findall(r"[a-z0-9_]+", text)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    chinese_bigrams = [
        "".join(chinese_chars[index:index + 2])
        for index in range(max(len(chinese_chars) - 1, 0))
    ]
    return words + chinese_bigrams
