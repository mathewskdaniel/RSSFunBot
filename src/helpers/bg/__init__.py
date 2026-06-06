# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from ._helper import BgHelper
from ._decorator import BgDecorator

__all__ = ['BgHelper', 'BgDecorator', 'bg']

bg = BgDecorator()
