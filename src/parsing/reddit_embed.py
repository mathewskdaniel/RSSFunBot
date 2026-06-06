# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

# Hosts Reddit commonly links to via the [link] anchor in RSS.
# Telegram renders native link previews for most of these when sent as bare URLs.
_EMBED_VIDEO_RE = re.compile(
    r'^https?://(?:'
    # YouTube
    r'(?:www\.|m\.)?youtube\.com/(?:watch|shorts|live)(?:[/?#]|$)'
    r'|youtu\.be/'
    # Vimeo
    r'|(?:www\.)?vimeo\.com/\d+'
    # Twitch
    r'|(?:www\.)?twitch\.tv/videos/\d+'
    r'|(?:www\.)?twitch\.tv/[^/]+/clip/'
    r'|clips\.twitch\.tv/'
    # Streamable, Dailymotion
    r'|(?:www\.)?streamable\.com/[\w-]+'
    r'|(?:www\.)?dailymotion\.com/video/'
    # TikTok (increasingly common on Reddit)
    r'|(?:www\.|vm\.)?tiktok\.com/'
    r')',
    re.IGNORECASE,
)

_YOUTUBE_HOSTS = frozenset({'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be'})


def is_embed_video_url(url: str) -> bool:
    return bool(url and _EMBED_VIDEO_RE.match(url.strip()))


def canonical_embed_url(url: str) -> str:
    """Return a stable URL suitable for Telegram link previews."""
    url = url.strip()
    parsed = urlparse(url)
    host = (parsed.netloc or '').lower()

    if host in _YOUTUBE_HOSTS or host == 'youtu.be':
        if host == 'youtu.be':
            video_id = parsed.path.lstrip('/').split('/')[0]
            if video_id:
                return f'https://www.youtube.com/watch?v={video_id}'
        if parsed.path.rstrip('/').endswith('/shorts'):
            video_id = parsed.path.rstrip('/').split('/')[-1]
            if video_id and video_id != 'shorts':
                return f'https://www.youtube.com/watch?v={video_id}'
        query = parse_qs(parsed.query, keep_blank_values=False)
        video_id = (query.get('v') or [None])[0]
        if video_id:
            clean_query = urlencode({'v': video_id})
            return urlunparse(('https', 'www.youtube.com', '/watch', '', clean_query, ''))

    # Drop tracking noise; keep path/query that identify the video.
    return urlunparse((parsed.scheme or 'https', parsed.netloc, parsed.path, '', parsed.query, ''))
