# Slack Bot

This directory contains a small FastAPI app that backs a few Slack slash commands for incident creation and database lookup simulation.

- The incident command opens a modal, collects a few incident details, creates a new Slack channel, invites the requester, and posts an announcement into a selected channel.
- The database lookup command simulates fetching data from an internal database and posting it back to the user in Slack.

This is just an example of how you could build out slash commands in Slack and integrate them with internal tools & data, or to add useful utilities and automation for your team without having to pay for third-party services.

It uses ngrok to expose the local API to the internet, so we can have Slack send requests to it and actually test it out. In production, you wouldn't need ngrok and instead the API would just be hosted on a publically available URL on your infrastructure.

## Current Flow

When someone runs `/create-incident` in Slack:

1. Slack sends a form-encoded request to `POST /slack/incident`
1. The app verifies the Slack request signature
1. The app opens a modal with:
   - incident title
   - severity
   - announcement channel
   - short description
1. Slack submits the modal to `POST /slack/interactive`
1. The app verifies the signature again
1. The app creates a new incident channel
1. The app invites the person who submitted the modal
1. The app posts a kickoff message in the new incident channel
1. The app posts an announcement in the selected channel

## Environment Variables

Create `slack/bot/.env` with values like:

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_INCIDENT_ANNOUNCE_CHANNEL_ID=C0AF8GADELC
NGROK_TOKEN=...
```

What each variable is for:

- `SLACK_BOT_TOKEN`: Bot User OAuth token from Slack
- `SLACK_SIGNING_SECRET`: signing secret from Slack app credentials
- `SLACK_INCIDENT_ANNOUNCE_CHANNEL_ID`: fallback announcement channel ID
- `NGROK_TOKEN`: ngrok auth token for creating public tunnels

The bot currently includes two hardcoded announcement channel options in the modal:

- `#alerts` -> `C0AF8GADELC`
- `#general` -> `C02NMC1DBH6`

It might be possible to make this dynamic by fetching the channel list from Slack, but that would require additional API scopes and logic to handle pagination, so for simplicity this example just uses hardcoded values.

## Local Development

From `slack/bot`:

```bash
uv sync
uv run uvicorn main:app --reload --env-file .env
```

That starts the local API on `http://127.0.0.1:8000`.

## ngrok Setup

To let Slack reach your local machine, expose the local FastAPI server over HTTPS with `ngrok`.

First, configure your auth token:

```bash
ngrok config add-authtoken $NGROK_TOKEN
```

Then start a tunnel to port `8000`:

```bash
ngrok http 8000
```

`ngrok` will print a public HTTPS URL that forwards traffic to your local app, for example:

```text
https://jeanne-nonnitric-andreas.ngrok-free.dev
```

Use that HTTPS base URL in the Slack app settings.

## Slack App Setup

### 1. Create Or Open A Slack App

In the Slack developer console, create an app or open the existing one tied to this bot.

### 2. Add The Slash Command

Under `Slash Commands`:

- Command: `/create-incident`
- Request URL: `https://<your-ngrok-domain>/slack/incident`
- Short description: `Create a new incident`

### 3. Enable Interactivity

Under `Interactivity & Shortcuts`:

- Turn Interactivity on
- Request URL: `https://<your-ngrok-domain>/slack/interactive`

The modal submit flow will not work without this.

### 4. Add OAuth Scopes

Under `OAuth & Permissions`, add bot token scopes:

- `commands`
- `chat:write`
- `channels:manage`
- `channels:write.invites`
- `chat:write.public`

### 5. Copy App Credentials

From Slack app settings:

- `Basic Information` -> copy the `Signing Secret`
- `OAuth & Permissions` -> copy the Bot User OAuth Token

Paste those into `.env` as `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN`.

## Channel Access Notes

The bot needs permission to post in the announcement channels you choose.

- If a channel is private, invite the bot to it
- If a channel is public, inviting the bot is still a safe default
- Some workspaces restrict posting in `#general`, even when the bot is present

If posting to a selected channel fails, check the app logs for the Slack API error.

## Running End-To-End Locally

1. Start the API:

```bash
uv run uvicorn main:app --reload --env-file .env
```

2. Start `ngrok`:

```bash
ngrok http 8000
```

3. Copy the HTTPS `ngrok` URL

1. Update Slack settings:

   - slash command request URL -> `https://<ngrok>/slack/incident`
   - interactivity request URL -> `https://<ngrok>/slack/interactive`

1. Run `/create-incident` in Slack

1. Submit the modal and confirm:

   - a new incident channel is created
   - you are invited to it
   - a kickoff message appears in the incident channel
   - an announcement appears in the selected destination channel

## Behavior Notes

- If no title text is supplied, the modal starts with a default like `incident-example-20260406`
- Channel names are normalized for Slack channel naming rules
- The incident creation work happens in a FastAPI background task so the Slack request can return quickly
- Slack request signature verification is enabled on both Slack endpoints

## Examples

<img width="630" height="647" alt="Image" src="https://github.com/user-attachments/assets/20090743-fafe-4b9c-b6f4-9e989a9efd63" />

<img width="1354" height="868" alt="Image" src="https://github.com/user-attachments/assets/d115c4b3-e0f5-41f5-81a2-4d1e77373bf5" />

<img width="809" height="448" alt="Image" src="https://github.com/user-attachments/assets/401f1710-7e86-4278-8e74-28a70ae73d8f" />
