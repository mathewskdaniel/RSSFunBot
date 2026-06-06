# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from __future__ import annotations
from typing import Optional

from telethon import Button
from telethon.tl import types
from telethon.tl.patched import Message

from .. import db, env
from ..i18n import i18n
from . import inner
from .types import *
from .utils import (
    command_gatekeeper, parse_command, escape_html, parse_callback_data_with_page,
    send_success_and_failure_msg, get_callback_tail, check_sub_limit,
)


@command_gatekeeper(only_manager=False)
async def cmd_sub(
        event: TypeEventMsgHint,
        *_,
        lang: Optional[str] = None,
        chat_id: Optional[int] = None,
        **__,
):
    chat_id = chat_id or event.chat_id

    await check_sub_limit(event, user_id=chat_id, lang=lang)

    args = parse_command(event.raw_text)
    filtered_urls = inner.utils.filter_urls(args)

    allow_reply = (event.is_private or event.is_group) and chat_id == event.chat_id
    prompt = (
        i18n[lang]['sub_reply_feed_url_prompt_html']
        if allow_reply
        else i18n[lang]['sub_usage_in_channel_html']
    )

    if not filtered_urls:
        await event.respond(
            prompt,
            parse_mode='html',
            buttons=(
                Button.force_reply(
                    single_use=True,
                    selective=True,
                    placeholder='url1 url2 url3 ...'
                )
                # do not force reply in private chat
                if event.is_group
                else None
            ),
            reply_to=event.id if event.is_group else None
        )
        return

    # delete the force reply message
    reply_message: Optional[Message] = await event.get_reply_message()
    if (
            reply_message
            and reply_message.sender_id == env.bot_id
            and isinstance(reply_message.reply_markup, types.ReplyKeyboardForceReply)
    ):
        env.loop.create_task(reply_message.delete())

    msg: Message = await event.respond(i18n[lang]['processing'])

    sub_result = await inner.sub.subs(chat_id, filtered_urls, lang=lang)

    if sub_result is None:
        await msg.edit(prompt, parse_mode='html')
        return

    await send_success_and_failure_msg(msg, **sub_result, lang=lang, edit=True)


@command_gatekeeper(only_manager=False)
async def cmd_unsub(
        event: TypeEventMsgHint,
        *_,
        lang: Optional[str] = None,
        chat_id: Optional[int] = None,
        **__,
):
    chat_id = chat_id or event.chat_id
    callback_tail = get_callback_tail(event, chat_id)
    args = parse_command(event.raw_text)

    unsub_result = await inner.sub.unsubs(chat_id, args, lang=lang)

    if unsub_result is None:
        buttons = await inner.utils.get_sub_choosing_buttons(
            chat_id, lang=lang,
            page_number=1, callback='unsub', get_page_callback='get_unsub_page', tail=callback_tail,
        )
        await event.respond(
            i18n[lang]['unsub_choose_sub_prompt_html'] if buttons else i18n[lang]['no_subscription'],
            buttons=buttons,
            parse_mode='html',
        )
        return

    await send_success_and_failure_msg(event, **unsub_result, lang=lang, edit=False)


@command_gatekeeper(only_manager=False)
async def cmd_or_callback_unsub_all(
        event: TypeEventCollectionMsgOrCb,
        *_,
        lang: Optional[str] = None,
        chat_id: Optional[int] = None,
        **__,
):  # command = /unsub_all, callback data = unsub_all
    chat_id = chat_id or event.chat_id
    callback_tail = get_callback_tail(event, chat_id)
    is_callback = isinstance(event, TypeEventCb)
    if is_callback:
        backup_file = await inner.sub.export_opml(chat_id)
        if backup_file is None:
            await event.respond(i18n[lang]['no_subscription'])
            return
        await event.respond(
            file=backup_file,
            attributes=(
                types.DocumentAttributeFilename("RSSFunBot_unsub_all_backup.opml"),
            ),
        )

        unsub_all_result = await inner.sub.unsub_all(chat_id, lang=lang)
        await send_success_and_failure_msg(event, **unsub_all_result, lang=lang, edit=True)
        return

    if await inner.utils.have_subs(chat_id):
        await event.respond(
            i18n[lang]['unsub_all_confirm_prompt'],
            buttons=[
                [Button.inline(i18n[lang]['unsub_all_confirm'], data=f'unsub_all{callback_tail}')],
                [Button.inline(i18n[lang]['unsub_all_cancel'], data='cancel')],
            ],
        )
        return
    await event.respond(i18n[lang]['no_subscription'])


@command_gatekeeper(only_manager=False)
async def cmd_list_or_callback_get_list_page(
        event: TypeEventCollectionMsgOrCb,
        *_,
        lang: Optional[str] = None,
        chat_id: Optional[int] = None,
        page_number: Optional[int] = None,
        **__,
):  # command = /list, callback data = get_list_page|{page_number}
    chat_id = chat_id or event.chat_id
    callback_tail = get_callback_tail(event, chat_id)
    is_callback = isinstance(event, TypeEventCb)
    if page_number is None:
        if is_callback and event.data.startswith('get_list_page'):
            _, page_number = parse_callback_data_with_page(event.data)
        else:
            page_number = 1

    buttons = await inner.utils.get_sub_list_buttons(
        chat_id, page_number=page_number, lang=lang,
        get_page_callback='get_list_page',
        tail=callback_tail,
    )

    if buttons is None:
        await event.respond(i18n[lang]['no_subscription'])
        return

    list_result = i18n[lang]['list_choose_sub_prompt']

    await (
        event.edit(list_result, buttons=buttons)
        if is_callback
        else event.respond(list_result, buttons=buttons)
    )


@command_gatekeeper(only_manager=False)
async def callback_list_toggle_sub(
        event: TypeEventCb,
        *_,
        lang: Optional[str] = None,
        chat_id: Optional[int] = None,
        **__,
):  # callback data = list_toggle={sub_id}|{page}
    chat_id = chat_id or event.chat_id
    sub_id, page = parse_callback_data_with_page(event.data)
    sub_id = int(sub_id)

    sub = await db.Sub.get_or_none(id=sub_id, user=chat_id).prefetch_related('feed')
    if sub is None:
        await event.answer('ERROR: ' + i18n[lang]['subscription_not_exist'], alert=True)
        return

    activate = sub.state != 1
    await inner.utils.activate_or_deactivate_sub(chat_id, sub, activate=activate)
    await event.answer(
        i18n[lang]['status_activated' if activate else 'status_deactivated'],
        alert=False,
    )
    await cmd_list_or_callback_get_list_page.__wrapped__(
        event, lang=lang, chat_id=chat_id, page_number=page,
    )


@command_gatekeeper(only_manager=False)
async def callback_unsub(
        event: TypeEventCb,
        *_,
        lang: Optional[str] = None,
        chat_id: Optional[int] = None,
        **__,
):  # callback data = unsub={sub_id}|{page}
    chat_id = chat_id or event.chat_id
    sub_id, page = parse_callback_data_with_page(event.data)
    sub_id = int(sub_id)

    unsub_result = await inner.sub.unsubs(chat_id, sub_ids=(sub_id,), lang=lang)

    if unsub_result['success_count']:  # successfully unsubed
        await callback_get_unsub_page.__wrapped__(event, lang=lang, page=page, chat_id=chat_id)

    await send_success_and_failure_msg(event, **unsub_result, lang=lang, edit=False)


@command_gatekeeper(only_manager=False)
async def callback_get_unsub_page(
        event: TypeEventCb,
        *_,
        page: Optional[int] = None,
        lang: Optional[str] = None,
        chat_id: Optional[int] = None,
        **__,
):  # callback data = get_unsub_page|{page_number}
    chat_id = chat_id or event.chat_id
    callback_tail = get_callback_tail(event, chat_id)
    if not page:
        _, page = parse_callback_data_with_page(event.data)
    buttons = await inner.utils.get_sub_choosing_buttons(
        chat_id, page, callback='unsub',
        get_page_callback='get_unsub_page', lang=lang, tail=callback_tail,
    )
    await event.edit(None if buttons else i18n[lang]['no_subscription'], buttons=buttons)
