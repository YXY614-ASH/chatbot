import unittest

import client
import config


class ClientMessageTests(unittest.TestCase):
    def test_mode_names_include_default_mode(self):
        self.assertIn(config.DEFAULT_MODE, client.get_mode_names())

    def test_structured_mode_uses_json_prompt(self):
        messages = client._build_messages(
            "解释一道欧姆定律题",
            [],
            "结构化题目解析",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("只输出一个 JSON 对象", messages[0]["content"])
        self.assertEqual(messages[-1], {"role": "user", "content": "解释一道欧姆定律题"})

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


if __name__ == "__main__":
    unittest.main()
