from flask import Blueprint, abort, render_template, send_from_directory

from app.content_loader import CATEGORIES
from app.posts import (
    get_asset_dir_for_slug,
    get_post_by_slug,
    get_post_neighbors,
    get_posts,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", posts=get_posts()[:3], active_nav="home")


@main_bp.route("/articles")
def articles():
    return render_template(
        "articles.html",
        posts=get_posts(),
        categories=CATEGORIES,
        active_nav="articles",
    )


@main_bp.route("/about")
def about():
    return render_template("about.html", active_nav="about")


@main_bp.route("/links")
def links():
    return render_template("links.html", active_nav="links")


@main_bp.route("/content/<slug>/<path:filename>")
def content_asset(slug, filename):
    asset_dir = get_asset_dir_for_slug(slug)
    if asset_dir is None:
        abort(404)

    safe_root = asset_dir.resolve()
    target = (asset_dir / filename).resolve()
    if not str(target).startswith(str(safe_root)) or not target.is_file():
        abort(404)

    return send_from_directory(asset_dir, filename)


@main_bp.route("/post/<slug>")
def post(slug):
    article = get_post_by_slug(slug)
    if article is None:
        abort(404)
    prev_post, next_post = get_post_neighbors(slug)
    return render_template(
        "post.html",
        post=article,
        prev_post=prev_post,
        next_post=next_post,
        active_nav=None,
    )
