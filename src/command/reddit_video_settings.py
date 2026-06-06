# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from __future__ import annotations
from contextlib import suppress
from typing import Optional

from telethon import Button
from telethon.errors import MessageNotModifiedError

from .. import db, env
from .. import reddit_video_config
from ..i18n import i18n
from .utils import command_gatekeeper, logger
from .types import *

HEIGHT_OPTIONS = (360, 480, 720)
SIZE_OPTIONS = (10_485_760, 20_971_520, 41_943_040, 52_428_800)
TIMEOUT_OPTIONS = (60, 120, 180, 300)

TEMP_DIR_PRESETS = (
    'config/media-temp',
    '/var/tmp/rssfunbot-media',
    '/tmp/rssfunbot-media',
)


def _resolve_temp_dir_preset(index: int) -> str:
    preset = TEMP_DIR_PRESETS[index % len(TEMP_DIR_PRESETS)]
    if preset == 'config/media-temp':
        from pathlib import Path
        return str((Path(env.config_folder_path) / 'media-temp').resolve())
    return preset


def _temp_dir_label(path: str) -> str:
    from pathlib import Path
    config_default = str((Path(env.config_folder_path) / 'media-temp').resolve())
    if path == config_default:
        return 'config/media-temp'
    if path == '/var/tmp/rssfunbot-media':
        return '/var/tmp/rssfunbot-media'
    if path == '/tmp/rssfunbot-media':
        return '/tmp/rssfunbot-media'
    return path


def _settings_text(lang: Optional[str]) -> str:
    enabled = reddit_video_config.is_enabled()
    height = reddit_video_config.max_height()
    max_bytes = reddit_video_config.max_bytes()
    timeout = reddit_video_config.download_timeout()
    temp_dir = reddit_video_config.media_temp_dir()
    return '\n'.join((
        f"<b>{i18n[lang]['reddit_video_settings_title']}</b>",
        '',
        f"{i18n[lang]['reddit_video_download']}: "
        f"<b>{i18n[lang]['reddit_video_on' if enabled else 'reddit_video_off']}</b>",
        f"{i18n[lang]['reddit_video_max_height']}: <b>{height}p</b>",
        f"{i18n[lang]['reddit_video_max_bytes']}: <b>{reddit_video_config.format_bytes(max_bytes)}</b>",
        f"{i18n[lang]['reddit_video_timeout']}: <b>{timeout}s</b>",
        f"{i18n[lang]['reddit_video_temp_dir']}: <code>{_temp_dir_label(temp_dir)}</code>",
        '',
        i18n[lang]['reddit_video_settings_hint_html'],
    ))


def _settings_buttons(lang: Optional[str]) -> tuple[tuple[Button, ...], ...]:
    enabled = reddit_video_config.is_enabled()
    height = reddit_video_config.max_height()
    max_bytes = reddit_video_config.max_bytes()
    timeout = reddit_video_config.download_timeout()
    return (
        (Button.inline(
            f"{'🔘' if enabled else '⚪'} {i18n[lang]['reddit_video_toggle']}",
            data='reddit_video=toggle',
        ),),
        tuple(
            Button.inline(
                f"{'🔘' if height == h else '⚪'} {h}p",
                data=f'reddit_video=height,{h}',
            )
            for h in HEIGHT_OPTIONS
        ),
        tuple(
            Button.inline(
                f"{'🔘' if max_bytes == s else '⚪'} {reddit_video_config.format_bytes(s)}",
                data=f'reddit_video=size,{s}',
            )
            for s in SIZE_OPTIONS
        ),
        tuple(
            Button.inline(
                f"{'🔘' if timeout == t else '⚪'} {t}s",
                data=f'reddit_video=timeout,{t}',
            )
            for t in TIMEOUT_OPTIONS
        ),
        tuple(
            Button.inline(
                f"{'🔘' if _temp_dir_label(reddit_video_config.media_temp_dir()) == label else '⚪'} {label}",
                data=f'reddit_video=temp,{idx}',
            )
            for idx, label in enumerate(('config/media-temp', '/var/tmp/rssfunbot-media', '/tmp/rssfunbot-media'))
        ),
        (Button.inline(i18n[lang]['reddit_video_reset_env'], data='reddit_video=reset'),),
        (Button.inline(i18n[lang]['cmd_description_help'], data='help'),),
    )


async def _render(event: TypeEventCollectionMsgOrCb, lang: Optional[str], *, edit: bool):
    text = _settings_text(lang)
    buttons = _settings_buttons(lang)
    if edit:
        try:
            await event.edit(text, parse_mode='html', buttons=buttons, link_preview=False)
        except MessageNotModifiedError:
            pass
    else:
        await event.respond(text, parse_mode='html', buttons=buttons, link_preview=False)


async def _answer_only(event: TypeEventCb):
    with suppress(Exception):
        await event.answer(cache_time=2)


@command_gatekeeper(only_manager=True, only_in_private_chat=False)
async def cmd_reddit_video(
        event: TypeEventMsgHint,
        *_,
        lang: Optional[str] = None,
        **__,
):
    await _render(event, lang, edit=False)


@command_gatekeeper(only_manager=True, only_in_private_chat=False)
async def callback_reddit_video(
        event: TypeEventCb,
        *_,
        lang: Optional[str] = None,
        **__,
):
    data = event.data.decode().strip().removeprefix('reddit_video=')
    action, _, arg = data.partition(',')

    if action in ('open', 'menu'):
        pass
    elif action == 'toggle':
        new_value = 0 if reddit_video_config.is_enabled() else 1
        await db.EffectiveOptions.set('reddit_video_download', new_value)
        logger.info(f'Reddit video download set to {new_value}')
    elif action == 'height' and arg.isdecimal():
        new_height = int(arg)
        if new_height == reddit_video_config.max_height():
            await _answer_only(event)
            return
        await db.EffectiveOptions.set('reddit_video_max_height', new_height)
        logger.info(f'Reddit video max height set to {arg}')
    elif action == 'size' and arg.isdecimal():
        new_size = int(arg)
        if new_size == reddit_video_config.max_bytes():
            await _answer_only(event)
            return
        await db.EffectiveOptions.set('reddit_video_max_bytes', new_size)
        logger.info(f'Reddit video max bytes set to {arg}')
    elif action == 'timeout' and arg.isdecimal():
        new_timeout = int(arg)
        if new_timeout == reddit_video_config.download_timeout():
            await _answer_only(event)
            return
        await db.EffectiveOptions.set('reddit_video_download_timeout', new_timeout)
        logger.info(f'Reddit video timeout set to {arg}')
    elif action == 'temp' and arg.isdecimal():
        path = _resolve_temp_dir_preset(int(arg))
        if path == reddit_video_config.media_temp_dir():
            await _answer_only(event)
            return
        await db.EffectiveOptions.set('media_temp_dir', path)
        logger.info(f'Reddit video temp dir set to {path}')
    elif action == 'reset':
        if all((
                reddit_video_config.is_enabled() == bool(env.REDDIT_VIDEO_DOWNLOAD),
                reddit_video_config.max_height() == env.REDDIT_VIDEO_MAX_HEIGHT,
                reddit_video_config.max_bytes() == env.REDDIT_VIDEO_MAX_BYTES,
                reddit_video_config.download_timeout() == env.REDDIT_VIDEO_DOWNLOAD_TIMEOUT,
                reddit_video_config.media_temp_dir() == env.MEDIA_TEMP_DIR,
        )):
            await _answer_only(event)
            return
        await db.EffectiveOptions.set('reddit_video_download', int(env.REDDIT_VIDEO_DOWNLOAD))
        await db.EffectiveOptions.set('reddit_video_max_height', env.REDDIT_VIDEO_MAX_HEIGHT)
        await db.EffectiveOptions.set('reddit_video_max_bytes', env.REDDIT_VIDEO_MAX_BYTES)
        await db.EffectiveOptions.set('reddit_video_download_timeout', env.REDDIT_VIDEO_DOWNLOAD_TIMEOUT)
        await db.EffectiveOptions.set('media_temp_dir', env.MEDIA_TEMP_DIR)
        logger.info('Reddit video settings reset to .env defaults')
    else:
        await event.answer(i18n[lang]['action_invalid'], cache_time=5)
        return

    with suppress(Exception):
        await event.answer()
    await _render(event, lang, edit=True)
