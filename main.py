from bot import run_bot
import logging
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(filename='brethren_bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info('Running main')
    run_bot()