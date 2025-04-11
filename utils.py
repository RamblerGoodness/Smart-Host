import logging
import time

def setup_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger("llm-wrapper")

logger = setup_logger()

def retry(func, retries=3, delay=1):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    raise Exception(f"Failed after {retries} retries.")
