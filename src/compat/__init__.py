# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from __future__ import annotations

import sys

if sys.version_info < (3, 9):
    raise RuntimeError("This bot requires Python 3.9 or later")

import listparser.opml

from .listparser_opml_mixin import OpmlMixin
from .utils import (
    INT64_T_MAX,
    nullcontext,
    AiohttpUvloopTransportHotfix,
    ssl_create_default_context,
    parsing_utils_html_validator_minify,
    cached_async,
    bozo_exception_removal_wrapper,
)

__all__ = [
    "INT64_T_MAX",
    "nullcontext",
    "AiohttpUvloopTransportHotfix",
    "ssl_create_default_context",
    "parsing_utils_html_validator_minify",
    "cached_async",
    "bozo_exception_removal_wrapper",
]

# Monkey-patching `listparser.opml.OpmlMixin` to support `text` and `title_orig`
# https://github.com/kurtmckee/listparser/issues/71
listparser.opml.OpmlMixin.start_opml_outline = OpmlMixin.start_opml_outline
