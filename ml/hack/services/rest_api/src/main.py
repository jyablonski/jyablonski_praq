import logging
# from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     logger.info("Loading ML models...")
#     topic_client = get_topic_client()
#     topic_client.load_model()

#     sentiment_client = get_sentiment_client()
#     sentiment_client.load_model()
#     logger.info("ML models loaded successfully")

#     # yield so app can run forever
#     yield

#     # Shutdown (cleanup if needed)
#     logger.info("Shutting down...")


app = FastAPI()

# app.include_router(v1_router, prefix="/v1")


# can conditionally include routers depending on env vars

# if os.getenv("ENABLE_EXPERIMENTAL_ROUTER", "false").lower() == "true":
#     app.include_router(experimental_router, prefix="/experimental")


@app.get("/")
async def root():
    return {"message": "Hello World"}
