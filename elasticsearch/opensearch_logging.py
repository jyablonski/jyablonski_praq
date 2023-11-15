import os
import logging
from opensearch_logger import OpenSearchHandler
import time
import random


def create_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(message)s",
        datefmt="%Y-%m-%d %I:%M:%S %p",
    )
    handler = OpenSearchHandler(
        index_name="python-aws-logs-big-tester",
        hosts=[f"{os.environ.get('OPENSEARCH_ENDPOINT')}:443"],
        # http_auth=("admin", "admin"),
        http_compress=True,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


# d = "https://search-jacobs-opensearch-cluster-cgil6crrqtd4ldap22kcf7htxu.us-east-1.es.amazonaws.com"
logger = create_logger()

logger.info("STARTING SCRIPT")
logger.info(f"TESTING {random.randint(1, 100)}")
logger.warning(f"ooof at {random.randint(1, 100)}")
logger.error(f"ERROR OOP {random.randint(1, 100)}")


time.sleep(5)
logger.info(f"TESTING {random.randint(1, 100)}")
