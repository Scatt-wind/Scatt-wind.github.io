import re
from pathlib import Path

import frontmatter
import markdown

CATEGORIES = ["项目介绍", "生活随笔", "踩坑记录"]

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"

_MD_EXTENSIONS = [
    "fenced_code",
    "tables",
    "sane_lists",
]

_IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _rewrite_image_paths(md_text: str, slug: str) -> str:
    def replacer(match: re.Match) -> str:
        alt = match.group(1)
        path = match.group(2).strip()
        if path.startswith(("http://", "https://", "/content/", "/static/")):
            return match.group(0)
        clean_path = path.lstrip("./")
        return f"![{alt}](/content/{slug}/{clean_path})"

    return _IMAGE_PATTERN.sub(replacer, md_text)


def _auto_excerpt(body: str, max_len: int = 120) -> str:
    text = _IMAGE_PATTERN.sub("", body)
    text = re.sub(r"[#*`\[\]()]", "", text)
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"


def _calc_reading_minutes(body: str) -> int:
    stripped = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", stripped))
    english_words = len(re.findall(r"[a-zA-Z]+", stripped))
    minutes = round(chinese_chars / 100 + english_words / 200)
    return max(1, minutes)


def _normalize_date(value) -> str:
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _normalize_tags(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _load_post(md_path: Path, category: str) -> dict | None:
    loaded = frontmatter.load(md_path)
    meta = loaded.metadata
    body = loaded.content

    title = meta.get("title")
    date = meta.get("date")
    if not title or not date:
        return None

    slug = meta.get("slug") or md_path.stem
    md_body = _rewrite_image_paths(body, slug)
    html = markdown.markdown(md_body, extensions=_MD_EXTENSIONS)

    reading_minutes = meta.get("reading_minutes")
    if reading_minutes is None:
        reading_minutes = _calc_reading_minutes(body)

    return {
        "slug": slug,
        "title": title,
        "excerpt": meta.get("excerpt") or _auto_excerpt(body),
        "date": _normalize_date(date),
        "category": category,
        "tags": _normalize_tags(meta.get("tags")),
        "reading_minutes": reading_minutes,
        "content": html,
        "_asset_dir": md_path.parent,
    }


def scan_posts() -> tuple[list[dict], dict[str, Path]]:
    posts: list[dict] = []
    asset_dirs: dict[str, Path] = {}

    if not CONTENT_ROOT.is_dir():
        return posts, asset_dirs

    for category in CATEGORIES:
        category_dir = CONTENT_ROOT / category
        if not category_dir.is_dir():
            continue
        for md_path in sorted(category_dir.glob("*.md")):
            post = _load_post(md_path, category)
            if post is None:
                continue
            asset_dirs[post["slug"]] = post.pop("_asset_dir")
            posts.append(post)

    posts.sort(key=lambda item: item["date"], reverse=True)
    return posts, asset_dirs


class PostStore:
    def __init__(self) -> None:
        self._posts: list[dict] = []
        self._slug_index: dict[str, dict] = {}
        self._asset_dirs: dict[str, Path] = {}
        self.reload()

    def reload(self) -> None:
        posts, asset_dirs = scan_posts()
        self._posts = posts
        self._slug_index = {post["slug"]: post for post in posts}
        self._asset_dirs = asset_dirs

    @property
    def posts(self) -> list[dict]:
        return self._posts

    def get_by_slug(self, slug: str) -> dict | None:
        return self._slug_index.get(slug)

    def get_asset_dir(self, slug: str) -> Path | None:
        return self._asset_dirs.get(slug)


_store: PostStore | None = None


def get_post_store() -> PostStore:
    global _store
    if _store is None:
        _store = PostStore()
    return _store
