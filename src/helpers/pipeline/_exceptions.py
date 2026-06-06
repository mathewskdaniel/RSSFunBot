# RSSFunBot
# https://github.com/mathewskdaniel/RSSFunBot

class StopPipeline(BaseException):
    def __init__(self, exception: BaseException = None, *args):
        super().__init__(*args)
        self.exception = exception
