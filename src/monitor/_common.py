# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

from typing import Final

from ..log import getLogger

TIMEOUT: Final[int] = 10 * 60  # 10 minutes

logger = getLogger('RSSFunBot.monitor')
