# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from __future__ import annotations

from pathlib import Path

from . import db, env


def _opt_int(key: str, fallback: int) -> int:
    try:
        return int(db.EffectiveOptions.get(key))
    except (RuntimeError, KeyError, TypeError, ValueError):
        return fallback


def _opt_str(key: str, fallback: str) -> str:
    try:
        value = db.EffectiveOptions.get(key)
        return str(value) if value else fallback
    except (RuntimeError, KeyError, TypeError, ValueError):
        return fallback


def is_enabled() -> bool:
    return bool(_opt_int('reddit_video_download', int(env.REDDIT_VIDEO_DOWNLOAD)))


def max_height() -> int:
    return max(220, min(720, _opt_int('reddit_video_max_height', env.REDDIT_VIDEO_MAX_HEIGHT)))


def max_bytes() -> int:
    return _opt_int('reddit_video_max_bytes', env.REDDIT_VIDEO_MAX_BYTES)


def download_timeout() -> int:
    return max(30, _opt_int('reddit_video_download_timeout', env.REDDIT_VIDEO_DOWNLOAD_TIMEOUT))


def media_temp_dir() -> str:
    path = _opt_str('media_temp_dir', env.MEDIA_TEMP_DIR)
    return str(Path(path).expanduser().resolve())


def format_bytes(num: int) -> str:
    if num >= 1048576:
        return f'{num / 1048576:.0f} MB'
    return f'{num / 1024:.0f} KB'
