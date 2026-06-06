# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from __future__ import annotations
from typing import Union

from telethon import events
from telethon.tl.patched import Message

__all__ = [
    'TypeEventMsg', 'TypeEventMsgHint', 'TypeEventCb', 'TypeEventInline', 'TypeEventChatAction',
    'TypeEventCollectionAll', 'TypeEventCollectionMsgLike', 'TypeEventCollectionMsgOrCb',
    'TypeEventCollectionMsgOrChatAction'
]

# Has: respond(), reply(), edit(), delete(), get_reply_message()
TypeEventMsg = events.NewMessage.Event
TypeEventMsgHint = Union[events.NewMessage.Event, Message]
# Has: respond(), reply(), edit(), delete(), answer()
TypeEventCb = events.CallbackQuery.Event
# Has: answer()
TypeEventInline = events.InlineQuery.Event
# Has: respond(), reply(), delete()
# Note: `events.ChatAction.Event` only have ChatGetter, do not have SenderGetter like others
TypeEventChatAction = events.ChatAction.Event

# All have: get_chat(), get_input_chat()
TypeEventCollectionAll = Union[
    events.NewMessage.Event, Message,  # Has: respond(), reply(), edit(), delete(), get_reply_message()
    events.CallbackQuery.Event,  # Has: respond(), reply(), edit(), delete(), answer()
    events.InlineQuery.Event,  # Has: answer()
    events.ChatAction.Event,  # Has: respond(), reply(), delete()
]
TypeEventCollectionMsgLike = Union[
    events.NewMessage.Event, Message,
    events.CallbackQuery.Event,
    events.ChatAction.Event,
]
TypeEventCollectionMsgOrCb = Union[
    events.NewMessage.Event, Message,
    events.CallbackQuery.Event,
]
TypeEventCollectionMsgOrChatAction = Union[
    events.NewMessage.Event, Message,
    events.ChatAction.Event,
]
