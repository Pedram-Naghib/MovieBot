from loguru import logger
from src import bot#, server
import os


if __name__ == "__main__":
    # server.run(host="0.0.0.0", port=8080)
    # logger.info("Bot Started")
    import src.responses
    bot.infinity_polling()