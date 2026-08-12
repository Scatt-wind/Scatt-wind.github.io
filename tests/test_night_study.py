import unittest

from app import create_app

HERO = "夜读，再写一行。"
HERO_SUB = "技术笔记 · 生活随笔"
TOKENS = {
    "--bg-primary": "#12151c",
    "--bg-secondary": "#181c24",
    "--text-primary": "#f3ebe1",
    "--text-secondary": "#9a8f82",
    "--text-muted": "#8a7f72",
    "--accent": "#8b3a2f",
    "--border": "#2c3340",
}


class NightStudyFrontendTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def _get(self, path):
        with self.client.get(path) as response:
            self.assertEqual(response.status_code, 200)
            return response.get_data(as_text=True)

    def test_base_shell_has_skip_link_logo_and_dot_nav(self):
        html = self._get("/")
        self.assertIn('class="skip-link"', html)
        self.assertIn('href="#main"', html)
        self.assertIn('id="main"', html)
        self.assertIn(">SGH</a>", html)
        self.assertNotIn("SGH-BLOG", html)
        self.assertIn("·", html)
        self.assertNotIn('class="nav-sep" aria-hidden="true">|</span>', html)
        self.assertIn("cdn.jsdelivr.net", html)
        self.assertIn("noto-serif-sc", html.lower())
        self.assertIn("noto-sans-sc", html.lower())
        self.assertNotIn("fonts.googleapis.com", html)

    def test_home_uses_ink_list_not_cards(self):
        html = self._get("/")
        self.assertIn(HERO, html)
        self.assertIn(HERO_SUB, html)
        self.assertNotIn("欢迎来到我的个人博客", html)
        self.assertIn('class="ink-list"', html)
        self.assertIn("ink-item--latest", html)
        self.assertNotIn("post-card", html)

    def test_article_page_is_narrow_night_read(self):
        home = self._get("/")
        marker = 'class="ink-item-link"'
        self.assertIn(marker, home)
        href_start = home.index("href=\"", home.index(marker)) + 6
        href_end = home.index("\"", href_start)
        post_path = home[href_start:href_end]
        html = self._get(post_path)
        self.assertIn('class="article-title-rule"', html)
        self.assertIn("article-nav-link", html)
        self.assertNotIn("nav-card", html)

    def test_articles_list_keeps_js_hooks(self):
        html = self._get("/articles")
        self.assertIn("article-item", html)
        self.assertIn("data-category=", html)
        self.assertIn("data-title=", html)
        self.assertIn("data-excerpt=", html)
        self.assertIn("data-tags=", html)
        self.assertIn('id="articles-search"', html)
        self.assertIn('id="pagination"', html)
        self.assertNotIn("article-item-card", html)

    def test_links_keep_existing_target(self):
        html = self._get("/links")
        self.assertIn("https://notes.kamacoder.com", html)
        self.assertIn("卡码笔记", html)

    def test_css_tokens_match_night_study(self):
        css = self._get("/static/css/style.css")
        for name, value in TOKENS.items():
            self.assertIn(name, css)
            self.assertIn(value, css)
        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertNotIn("--accent: #58a6ff", css)


if __name__ == "__main__":
    unittest.main()
