# uv run uvicorn main:app --reload --env-file .env

import hashlib
import hmac
import json
import logging
import os
import random
import re
import time
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = FastAPI()
logger = logging.getLogger(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
INCIDENT_ANNOUNCE_CHANNEL = os.environ.get("SLACK_INCIDENT_ANNOUNCE_CHANNEL_ID", "")

INCIDENT_MODAL_CALLBACK_ID = "create_incident_modal"
TITLE_BLOCK_ID = "incident_title"
TITLE_ACTION_ID = "value"
SEVERITY_BLOCK_ID = "incident_severity"
SEVERITY_ACTION_ID = "value"
ANNOUNCE_CHANNEL_BLOCK_ID = "incident_announce_channel"
ANNOUNCE_CHANNEL_ACTION_ID = "value"
DESCRIPTION_BLOCK_ID = "incident_description"
DESCRIPTION_ACTION_ID = "value"

ANNOUNCEMENT_CHANNELS = {
    "alerts": "C0AF8GADELC",
    "general": "C02NMC1DBH6",
}

client = WebClient(token=SLACK_BOT_TOKEN)


def require_signing_secret() -> None:
    if not SLACK_SIGNING_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Missing SLACK_SIGNING_SECRET environment variable.",
        )


def require_incident_settings() -> None:
    require_signing_secret()

    if not SLACK_BOT_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Missing SLACK_BOT_TOKEN environment variable.",
        )

    if not INCIDENT_ANNOUNCE_CHANNEL:
        raise HTTPException(
            status_code=500,
            detail="Missing SLACK_INCIDENT_ANNOUNCE_CHANNEL_ID environment variable.",
        )


async def verify_slack_request(request: Request) -> None:
    signature = request.headers.get("x-slack-signature")
    timestamp = request.headers.get("x-slack-request-timestamp")

    if not signature or not timestamp:
        raise HTTPException(status_code=401, detail="Missing Slack signature headers.")

    try:
        timestamp_int = int(timestamp)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid Slack timestamp.") from exc

    if abs(time.time() - timestamp_int) > 60 * 5:
        raise HTTPException(status_code=401, detail="Slack request timestamp is stale.")

    request_body = await request.body()
    basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}".encode("utf-8")
    computed_signature = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode("utf-8"),
            basestring,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(computed_signature, signature):
        raise HTTPException(status_code=401, detail="Invalid Slack request signature.")


def build_incident_name(raw_text: str) -> str:
    cleaned_text = raw_text.strip()
    if cleaned_text:
        return cleaned_text

    return f"incident-example-{datetime.now(UTC).strftime('%Y%m%d')}"


def build_channel_name(incident_name: str) -> str:
    normalized = incident_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9-_ ]", "", normalized)
    normalized = normalized.replace("_", "-").replace(" ", "-")
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")

    if not normalized:
        normalized = datetime.now(UTC).strftime("incident-%Y%m%d-%H%M%S").lower()

    if not normalized.startswith("inc-") and not normalized.startswith("incident-"):
        normalized = f"inc-{normalized}"

    return normalized[:80]


def build_incident_modal(initial_title: str, user_name: str) -> dict:
    metadata = {"user_name": user_name}
    announcement_options = [
        {
            "text": {"type": "plain_text", "text": f"#{channel_name}"},
            "value": channel_id,
        }
        for channel_name, channel_id in ANNOUNCEMENT_CHANNELS.items()
    ]
    default_channel_name, default_channel_id = next(iter(ANNOUNCEMENT_CHANNELS.items()))

    return {
        "type": "modal",
        "callback_id": INCIDENT_MODAL_CALLBACK_ID,
        "private_metadata": json.dumps(metadata),
        "title": {"type": "plain_text", "text": "Create incident"},
        "submit": {"type": "plain_text", "text": "Create"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": TITLE_BLOCK_ID,
                "label": {"type": "plain_text", "text": "Incident title"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": TITLE_ACTION_ID,
                    "initial_value": initial_title,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "API 500s on checkout",
                    },
                },
            },
            {
                "type": "input",
                "block_id": SEVERITY_BLOCK_ID,
                "optional": True,
                "label": {"type": "plain_text", "text": "Severity"},
                "element": {
                    "type": "static_select",
                    "action_id": SEVERITY_ACTION_ID,
                    "placeholder": {"type": "plain_text", "text": "Select severity"},
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "SEV1"},
                            "value": "SEV1",
                        },
                        {
                            "text": {"type": "plain_text", "text": "SEV2"},
                            "value": "SEV2",
                        },
                        {
                            "text": {"type": "plain_text", "text": "SEV3"},
                            "value": "SEV3",
                        },
                        {
                            "text": {"type": "plain_text", "text": "SEV4"},
                            "value": "SEV4",
                        },
                    ],
                },
            },
            {
                "type": "input",
                "block_id": ANNOUNCE_CHANNEL_BLOCK_ID,
                "optional": True,
                "label": {
                    "type": "plain_text",
                    "text": "Announcement channel",
                },
                "element": {
                    "type": "static_select",
                    "action_id": ANNOUNCE_CHANNEL_ACTION_ID,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select announcement channel",
                    },
                    "initial_option": {
                        "text": {
                            "type": "plain_text",
                            "text": f"#{default_channel_name}",
                        },
                        "value": default_channel_id,
                    },
                    "options": announcement_options,
                },
            },
            {
                "type": "input",
                "block_id": DESCRIPTION_BLOCK_ID,
                "label": {"type": "plain_text", "text": "Short description"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": DESCRIPTION_ACTION_ID,
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "What is broken, who is impacted, and what do responders need to know?",
                    },
                },
            },
        ],
    }


def extract_submission_value(view_state: dict, block_id: str, action_id: str) -> str:
    block_values = view_state["values"].get(block_id)
    if not block_values:
        return ""

    block = block_values.get(action_id)
    if not block:
        return ""

    if "value" in block:
        return block["value"].strip()

    selected_option = block.get("selected_option")
    if selected_option:
        return selected_option["value"].strip()

    return ""


def mask_email(email: str) -> str:
    local_part, domain = email.split("@", 1)
    return f"{'*' * len(local_part)}@{domain}"


def generate_mock_customer_record(email: str) -> dict:
    now = datetime.now(UTC)
    start = datetime(2026, 1, 1, tzinfo=UTC)
    random_epoch = random.randint(int(start.timestamp()), int(now.timestamp()))
    last_seen_at = datetime.fromtimestamp(random_epoch, tz=UTC)
    status = "active" if (now - last_seen_at).days <= 30 else "inactive"

    return {
        "customer_id": str(uuid4()),
        "email": mask_email(email),
        "plan": random.choice(["free", "enterprise"]),
        "status": status,
        "last_seen_at": last_seen_at.isoformat().replace("+00:00", "Z"),
    }


@app.post("/slack/db_lookup")
async def db_lookup_command(request: Request):
    require_signing_secret()
    await verify_slack_request(request)

    form = await request.form()
    query_text = str(form.get("text", "")).strip().lower()
    user_name = str(form.get("user_name", "unknown-user"))

    if not query_text:
        return {
            "response_type": "ephemeral",
            "text": (
                "Usage: `/db-lookup <email>`\nExample: `/db-lookup person@example.com`"
            ),
        }

    if "@" not in query_text or "." not in query_text.split("@", 1)[-1]:
        return {
            "response_type": "ephemeral",
            "text": (
                f":warning: `{query_text}` does not look like a valid email.\n"
                "Try: `/db-lookup person@example.com`"
            ),
        }

    record = generate_mock_customer_record(query_text)
    formatted_record = json.dumps(record, indent=2)
    return {
        "response_type": "ephemeral",
        "text": (
            f":mag: Lookup result requested by `{user_name}`.\n```{formatted_record}```"
        ),
    }


@app.post("/slack/incident")
async def open_incident_modal(
    request: Request,
):
    require_incident_settings()
    await verify_slack_request(request)

    form = await request.form()
    user_name = str(form["user_name"])
    trigger_id = str(form["trigger_id"])
    text = str(form.get("text", ""))

    initial_title = build_incident_name(text)

    try:
        client.views_open(
            trigger_id=trigger_id,
            view=build_incident_modal(initial_title=initial_title, user_name=user_name),
        )
    except SlackApiError as exc:
        error_message = exc.response.get("error", "unknown_error")
        logger.exception("Failed to open incident modal: %s", error_message)
        return {
            "response_type": "ephemeral",
            "text": f"Could not open the incident modal. Slack API error: `{error_message}`",
        }

    return Response(status_code=200)


@app.post("/slack/interactive")
async def submit_incident_modal(
    request: Request,
    background_tasks: BackgroundTasks,
):
    require_incident_settings()
    await verify_slack_request(request)

    form = await request.form()
    payload = str(form["payload"])
    interaction = json.loads(payload)

    if interaction.get("type") != "view_submission":
        return {}

    view = interaction["view"]
    if view.get("callback_id") != INCIDENT_MODAL_CALLBACK_ID:
        return {}

    metadata = json.loads(view.get("private_metadata") or "{}")
    user = interaction["user"]
    user_id = user["id"]
    user_name = (
        metadata.get("user_name") or user.get("username") or user.get("name", "")
    )

    incident_title = extract_submission_value(
        view_state=view["state"],
        block_id=TITLE_BLOCK_ID,
        action_id=TITLE_ACTION_ID,
    )
    severity = extract_submission_value(
        view_state=view["state"],
        block_id=SEVERITY_BLOCK_ID,
        action_id=SEVERITY_ACTION_ID,
    )
    announce_channel_id = extract_submission_value(
        view_state=view["state"],
        block_id=ANNOUNCE_CHANNEL_BLOCK_ID,
        action_id=ANNOUNCE_CHANNEL_ACTION_ID,
    )
    description = extract_submission_value(
        view_state=view["state"],
        block_id=DESCRIPTION_BLOCK_ID,
        action_id=DESCRIPTION_ACTION_ID,
    )

    background_tasks.add_task(
        handle_incident,
        user_id,
        user_name,
        incident_title,
        severity,
        announce_channel_id or INCIDENT_ANNOUNCE_CHANNEL,
        description,
    )

    return Response(status_code=200)


def handle_incident(
    user_id: str,
    user_name: str,
    incident_title: str,
    severity: str,
    announce_channel_id: str,
    description: str,
):
    channel_name = build_channel_name(incident_title)
    severity_line = f"Severity: *{severity}*\n" if severity else ""

    try:
        result = client.conversations_create(name=channel_name, is_private=False)
        channel_id = result["channel"]["id"]
        client.conversations_invite(channel=channel_id, users=user_id)
    except SlackApiError as exc:
        error_message = exc.response.get("error", "unknown_error")
        logger.exception("Failed to create incident resources: %s", error_message)
        post_best_effort_error(
            incident_title=incident_title,
            user_id=user_id,
            error_message=error_message,
        )
        return

    try:
        client.chat_postMessage(
            channel=channel_id,
            text=(
                f":rotating_light: Incident *{incident_title}* has been started.\n"
                f"{severity_line}"
                f"Incident lead: <@{user_id}> ({user_name})\n"
                f"Summary: {description}\n"
                "Use this channel for coordination, updates, and timeline notes."
            ),
        )
    except SlackApiError as exc:
        error_message = exc.response.get("error", "unknown_error")
        logger.exception("Failed to post incident kickoff message: %s", error_message)

    try:
        client.chat_postMessage(
            channel=announce_channel_id,
            text=(
                f":rotating_light: Incident *{incident_title}* has been started.\n"
                f"{severity_line}"
                f"Led by: <@{user_id}> ({user_name})\n"
                f"Summary: {description}\n"
                f"Channel: <#{channel_id}>"
            ),
        )
    except SlackApiError as exc:
        error_message = exc.response.get("error", "unknown_error")
        logger.exception(
            "Failed to post incident alert announcement to %s: %s",
            announce_channel_id,
            error_message,
        )


def post_best_effort_error(
    incident_title: str, user_id: str, error_message: str
) -> None:
    try:
        client.chat_postMessage(
            channel=INCIDENT_ANNOUNCE_CHANNEL,
            text=(
                f":warning: Failed to create incident *{incident_title}* for "
                f"<@{user_id}>. Slack API error: `{error_message}`"
            ),
        )
    except SlackApiError:
        logger.exception("Failed to post incident creation error to announce channel")
