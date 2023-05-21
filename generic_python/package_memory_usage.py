from memory_profiler import profile
from datetime import datetime, timedelta

# run -- python3 generic_python/package_memory_usage.py -- to see how much memory is being used by each package


@profile
def find_import_memory_usage():
    from datetime import datetime, timedelta
    import hashlib
    import logging
    import os
    import requests
    from typing import List, Optional
    import uuid

    import boto3
    from bs4 import BeautifulSoup
    from botocore.exceptions import ClientError
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    import numpy as np
    import pandas as pd
    import praw
    import requests
    from sqlalchemy import exc, create_engine
    from sqlalchemy.engine.base import Engine
    import sentry_sdk
    import tweepy
    from tweepy import OAuthHandler
    import opensearch_logger
    import awswrangler as wr


print(f"hello world at {datetime.now()}")
find_import_memory_usage()
