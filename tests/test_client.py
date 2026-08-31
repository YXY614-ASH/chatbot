import unittest

import client
import config
import document


class FakeDelta:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.delta = FakeDelta(content)


class FakeChunk:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return [FakeChunk("你"), FakeChunk("好")]


class FakeChat:
    def __init__(self):
        self.completions = FakeCompletions()


class FakeClient:
    def __init__(self):
        self.chat = FakeChat()


class ClientMessageTests(unittest.TestCase):
    def test_mode_names_include_default_mode(self):
        self.assertIn(config.DEFAULT_MODE, client.get_mode_names())
        self.assertIn("题目解析卡", client.get_mode_names())
        self.assertIn("学习计划卡", client.get_mode_names())

    def test_pdf_mode_accepts_context(self):
        messages = client._build_messages(
            "路线图下一步是什么？",
            [],
            "PDF资料问答",
            "⑤ Agent 是下一个要学的阶段。",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("PDF 资料片段", messages[0]["content"])
        self.assertIn("Agent", messages[0]["content"])
        self.assertEqual(messages[-1], {"role": "user", "content": "路线图下一步是什么？"})

    def test_tuple_history_is_converted_to_messages(self):
        messages = client._build_messages(
            "继续",
            [("什么是过拟合？", "过拟合是模型把训练数据记得太死。")],
            config.DEFAULT_MODE,
        )

        self.assertEqual(messages[1], {"role": "user", "content": "什么是过拟合？"})
        self.assertEqual(messages[2], {"role": "assistant", "content": "过拟合是模型把训练数据记得太死。"})
        self.assertEqual(messages[3], {"role": "user", "content": "继续"})

    def test_messages_history_is_kept(self):
        messages = client._build_messages(
            "再短一点",
            [
                {"role": "user", "content": "解释 RAG"},
                {"role": "assistant", "content": "RAG 是先检索资料再回答。"},
            ],
            config.DEFAULT_MODE,
        )

        self.assertEqual(messages[1], {"role": "user", "content": "解释 RAG"})
        self.assertEqual(messages[2], {"role": "assistant", "content": "RAG 是先检索资料再回答。"})
        self.assertEqual(messages[3], {"role": "user", "content": "再短一点"})

    def test_chat_stream_yields_accumulated_answer(self):
        original_client = client._client
        fake_client = FakeClient()
        client._client = fake_client
        try:
            outputs = list(client.chat_stream("打个招呼", [], "学习助手"))
        finally:
            client._client = original_client

        self.assertEqual(outputs, ["你", "你好"])

    def test_question_card_mode_uses_fixed_template(self):
        messages = client._build_messages(
            "电阻为 10 欧，电流为 2A，电压是多少？",
            [],
            "题目解析卡",
        )

        self.assertIn("# 题目解析卡", messages[0]["content"])
        self.assertIn("## 解题思路", messages[0]["content"])
        self.assertIn("## 最终答案", messages[0]["content"])

    def test_study_plan_mode_uses_fixed_template(self):
        messages = client._build_messages(
            "两周内入门 RAG",
            [],
            "学习计划卡",
        )

        self.assertIn("# 学习计划卡", messages[0]["content"])
        self.assertIn("## 阶段安排", messages[0]["content"])
        self.assertIn("## 每周行动清单", messages[0]["content"])

    def test_template_mode_uses_configured_temperature(self):
        original_client = client._client
        fake_client = FakeClient()
        client._client = fake_client
        try:
            list(client.chat_stream("两周内入门 RAG", [], "学习计划卡"))
        finally:
            client._client = original_client

        self.assertEqual(fake_client.chat.completions.last_kwargs["temperature"], 0.4)


class DocumentTests(unittest.TestCase):
    def test_retrieve_relevant_chunks_prefers_matching_text(self):
        chunks = [
            {"page": 1, "text": "Python 打底：变量、列表、字典、函数。"},
            {"page": 2, "text": "Agent 能调用工具，按步骤完成任务。"},
        ]

        result = document.retrieve_relevant_chunks("Agent 会做什么？", chunks, top_k=1)

        self.assertEqual(result[0]["page"], 2)

    def test_build_chunks_keeps_page_number(self):
        pages = [{"page": 3, "text": "RAG 让模型先查资料再回答。" * 80}]

        chunks = document.build_chunks(pages)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk["page"] == 3 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
