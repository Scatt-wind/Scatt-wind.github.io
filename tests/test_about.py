import re
import unittest

from app import create_app

INTRO = (
    "2 年大模型应用开发，方向是 RAG / Agent。"
    "做过不合格描述分类、质量标准知识库问答、异常多轮排查 Agent。"
)

SKILL_TILES = (
    ("rag", "RAG", "FAQ 命中 92%+ · 答对率 88%"),
    ("agent", "Agent", "LangGraph · 最多 8 轮"),
    ("classify", "文本分类", "BERT 94% · F1 0.93"),
    ("compress", "模型压缩", "量化 / 蒸馏 / 剪枝"),
    ("prompt", "Prompt + AI 编程", "Bad Case 迭代 · Cursor"),
)

FORBIDDEN = (
    "Dify",
    "Coze",
    "MCP",
    "智能投顾",
    "金融资讯",
    "honglanh6765@gmail.com",
    "召回率 90%",
    "代码成功率 95%",
    "8.3",
    "20 万级",
    "体积 -62%",
    "效率 +40%",
    "1.5 年",
    "广东特拓",
    "广州软件学院",
)


class AboutPageTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def _html(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        return response.get_data(as_text=True)

    def test_intro_matches_resume_summary(self):
        html = self._html()
        self.assertIn(INTRO, html)

    def test_email_is_163_not_gmail(self):
        html = self._html()
        self.assertIn("13208281328@163.com", html)
        self.assertNotIn("honglanh6765@gmail.com", html)
        phone_hits = re.findall(r"13208281328(?!@163\.com)", html)
        self.assertEqual(phone_hits, [])

    def test_keeps_name_tagline_and_hobbies(self):
        html = self._html()
        self.assertIn("SGH", html)
        self.assertIn("用代码解决问题，用文字记录生活", html)
        self.assertIn("CS2 双平台 S 分段", html)
        self.assertIn("软笔书法（国家十级）", html)
        self.assertIn("打篮球", html)

    def test_skill_tiles_and_templates_align(self):
        html = self._html()
        for skill_id, title, metric in SKILL_TILES:
            self.assertIn(f'data-skill="{skill_id}"', html)
            self.assertIn(f'id="skill-detail-{skill_id}"', html)
            self.assertIn(title, html)
            self.assertIn(metric, html)
        self.assertNotIn('data-skill="deploy"', html)
        self.assertNotIn('data-skill="data"', html)

    def test_skill_details_include_resume_facts(self):
        html = self._html()
        self.assertIn("FAQ 命中准确率 92%+", html)
        self.assertIn("整体答对率从 75% 提到 88%", html)
        self.assertIn("LangGraph", html)
        self.assertIn("最多 8 轮", html)
        self.assertIn("BERT 准确率 94%、F1 0.93", html)
        self.assertIn("学生模型是 BiLSTM", html)
        self.assertIn("Cursor、Claude Code", html)

    def test_old_copy_and_employer_are_absent(self):
        html = self._html()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, html)


if __name__ == "__main__":
    unittest.main()
