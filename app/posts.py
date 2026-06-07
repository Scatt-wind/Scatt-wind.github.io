from app.content_loader import CATEGORIES, get_post_store


def get_posts():
    return get_post_store().posts


def get_post_by_slug(slug):
    return get_post_store().get_by_slug(slug)


def get_asset_dir_for_slug(slug):
    return get_post_store().get_asset_dir(slug)


def get_post_neighbors(slug):
    posts = get_posts()
    slugs = [post["slug"] for post in posts]
    try:
        idx = slugs.index(slug)
    except ValueError:
        return None, None
    prev_post = posts[idx + 1] if idx + 1 < len(posts) else None
    next_post = posts[idx - 1] if idx > 0 else None
    return prev_post, next_post
