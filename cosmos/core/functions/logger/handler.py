from cosmos.core.functions.logger.logger import Logger


class LoggerHandler(Logger):

    def __init__(self, bot):
        self.bot = bot
        super().__init__(self.bot)
        self.set_file_handler()
