# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
import uuid
from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from .. import env
from .. import reddit_video_config

logger = logging.getLogger('RSSFunBot.reddit_video')

V_REDD_IT_RE = re.compile(
    r'^https?://(?:www\.)?v\.redd\.it/(?P<id>[A-Za-z0-9]+)/?$',
    re.IGNORECASE,
)
REDDIT_PREVIEW_RE = re.compile(
    r'^https?://(?:external-preview|preview)\.redd\.it/',
    re.IGNORECASE,
)
REDDIT_PREVIEW_IMAGE_RE = re.compile(
    r'^https?://preview\.redd\.it/(?P<path>[^?]+)',
    re.IGNORECASE,
)

@dataclass
class RedditVideoFile:
    path: str
    duration: int = 0
    width: int = 0
    height: int = 0


def is_v_redd_it(url: str) -> bool:
    return bool(url and V_REDD_IT_RE.match(url.strip()))


def is_reddit_preview_image(url: str) -> bool:
    return bool(url and REDDIT_PREVIEW_RE.match(url.strip()))


def full_image_url(url: str) -> str | None:
    """Map Reddit RSS preview thumbnails to full-resolution i.redd.it sources."""
    if not url:
        return None
    match = REDDIT_PREVIEW_IMAGE_RE.match(url.strip())
    if not match:
        return None
    return f'https://i.redd.it/{match.group("path")}'


def v_redd_it_id(url: str) -> str | None:
    match = V_REDD_IT_RE.match(url.strip())
    return match.group('id') if match else None


def hls_playlist_url(video_id: str) -> str:
    return f'https://v.redd.it/{video_id}/HLSPlaylist.m3u8'


def _ytdlp_format(max_height: int) -> str:
    return f'bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best'


def unlink_local(path: str | None) -> None:
    if not path:
        return
    with suppress(OSError):
        os.unlink(path)


def probe_mp4(path: str) -> tuple[int, int, int]:
    """Return (duration_seconds, width, height)."""
    import subprocess

    try:
        proc = subprocess.run(
            [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-show_format', path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 0, 0, 0
    if proc.returncode != 0 or not proc.stdout:
        return 0, 0, 0

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return 0, 0, 0

    duration = 0
    with suppress(TypeError, ValueError):
        duration = int(float(data.get('format', {}).get('duration', 0)))

    width = height = 0
    for stream in data.get('streams', []):
        if stream.get('codec_type') != 'video':
            continue
        with suppress(TypeError, ValueError):
            width = int(stream.get('width') or 0)
            height = int(stream.get('height') or 0)
        break

    return duration, width, height


def _download_sync(source_url: str, output_path: str, max_height: int) -> tuple[bool, str]:
    import subprocess

    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--no-playlist',
        '--no-warnings',
        '-f', _ytdlp_format(max_height),
        '--merge-output-format', 'mp4',
        '-o', output_path,
        source_url,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=reddit_video_config.download_timeout(),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, 'yt-dlp timeout'
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or '').strip()[-500:]
        return False, err or f'yt-dlp exit {proc.returncode}'
    if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
        return False, 'empty output file'
    return True, ''


async def download_v_redd_it(url: str) -> RedditVideoFile | None:
    """
    Download Reddit-hosted video (video+audio merged) to a temp file.
    Caller must delete path when done.
    """
    if not reddit_video_config.is_enabled():
        return None
    video_id = v_redd_it_id(url)
    if not video_id:
        return None

    temp_dir = Path(reddit_video_config.media_temp_dir())
    temp_dir.mkdir(parents=True, exist_ok=True)
    out_path = str(temp_dir / f'reddit_{video_id}_{uuid.uuid4().hex[:12]}.mp4')
    source_url = hls_playlist_url(video_id)

    loop = asyncio.get_running_loop()
    ok, reason = await loop.run_in_executor(
        None,
        partial(_download_sync, source_url, out_path, reddit_video_config.max_height()),
    )
    if not ok:
        logger.info(f'Reddit video download failed: {url} ({reason})')
        unlink_local(out_path)
        return None

    size = os.path.getsize(out_path)
    max_bytes = reddit_video_config.max_bytes()
    if size > max_bytes:
        logger.info(f'Reddit video too large ({size} > {max_bytes}): {url}')
        unlink_local(out_path)
        return None

    duration, width, height = probe_mp4(out_path)
    logger.info(
        f'Downloaded Reddit video ({size / 1024 / 1024:.2f}MB, '
        f'{width}x{height}, {duration}s): {url}'
    )
    return RedditVideoFile(path=out_path, duration=duration, width=width, height=height)
