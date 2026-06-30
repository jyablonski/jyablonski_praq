import os
import random
import time

from jyablonski_common_modules.logging import create_logger

logger = create_logger(
    es_index="where-da-index-at",
    es_host_endpoint=os.environ.get("OPENSEARCH_ENDPOINT"),
)

logger.info("STARTING SCRIPT")
logger.info(f"TESTING {random.randint(1, 100)}")
logger.warning(f"ooof at {random.randint(1, 100)}")
logger.error(f"ERROR OOP {random.randint(1, 100)}")


time.sleep(5)
logger.info(f"TESTING try this {random.randint(1, 100)}")
