import logging
import threading
import time

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.content_loader import CONTENT_ROOT, get_post_store

logger = logging.getLogger(__name__)

_RELOAD_SUFFIXES = {".md", ".markdown", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


class ContentReloadHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_reload = 0.0
        self._debounce_seconds = 0.4

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = event.src_path
        if not any(path.lower().endswith(suffix) for suffix in _RELOAD_SUFFIXES):
            return
        self._schedule_reload()

    def _schedule_reload(self) -> None:
        with self._lock:
            now = time.monotonic()
            if now - self._last_reload < self._debounce_seconds:
                return
            self._last_reload = now
        get_post_store().reload()
        logger.info("Content reloaded from %s", CONTENT_ROOT)


def start_content_watcher() -> Observer | None:
    if not CONTENT_ROOT.is_dir():
        return None

    handler = ContentReloadHandler()
    observer = Observer()
    observer.schedule(handler, str(CONTENT_ROOT), recursive=True)
    observer.start()
    logger.info("Watching content directory: %s", CONTENT_ROOT)
    return observer
