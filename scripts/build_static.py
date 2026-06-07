"""Pre-render Flask routes to static HTML for GitHub Pages."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist"

sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from app.posts import get_asset_dir_for_slug, get_posts  # noqa: E402

STATIC_ROUTES = ["/", "/articles", "/about", "/links"]


def route_to_output_path(route: str) -> Path:
    route = route.rstrip("/") or "/"
    if route == "/":
        return OUTPUT / "index.html"
    return OUTPUT / route.lstrip("/") / "index.html"


def save_response(route: str, response) -> None:
    if response.status_code != 200:
        raise RuntimeError(f"Failed to render {route}: HTTP {response.status_code}")

    out_path = route_to_output_path(route)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(response.data)
    print(f"  {route} -> {out_path.relative_to(ROOT)}")


def copy_static_assets() -> None:
    src = ROOT / "app" / "static"
    dest = OUTPUT / "static"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"  static/ -> {dest.relative_to(ROOT)}")


def copy_post_assets() -> None:
    for post in get_posts():
        slug = post["slug"]
        asset_dir = get_asset_dir_for_slug(slug)
        if asset_dir is None or not asset_dir.is_dir():
            continue

        copied = 0
        for path in asset_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() == ".md":
                continue
            rel = path.relative_to(asset_dir)
            dest = OUTPUT / "content" / slug / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            copied += 1

        if copied:
            print(f"  content/{slug}/ ({copied} files)")


def build() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()

    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    print("Rendering pages:")
    for route in STATIC_ROUTES:
        save_response(route, client.get(route))

    for post in get_posts():
        route = f"/post/{post['slug']}"
        save_response(route, client.get(route))

    print("Copying assets:")
    copy_static_assets()
    copy_post_assets()

    (OUTPUT / ".nojekyll").touch()
    shutil.copy2(OUTPUT / "index.html", OUTPUT / "404.html")
    print(f"  404.html (from index.html)")

    print(f"\nBuild complete: {OUTPUT}")


if __name__ == "__main__":
    build()
