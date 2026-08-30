import unittest

import client
import config
import document


class ClientMessageTests(unittest.TestCase):
    def test_mode_names_include_default_mode(self):
        self.assertIn(config.DEFAULT_MODE, client.get_mode_names())

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
