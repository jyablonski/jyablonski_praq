import os
from typing import Any

import requests


# additional work needed to properly setup dedup keys and things like that
# might be easier with a dedicated pagerduty package
def trigger_incident(
    routing_key: str,
    event_title: str,
    source: str,
    severity: str,
    details: dict[str, Any] = {},
) -> None:
    """
    Function to trigger Pagerduty Incidents.  Requires Routing Key (labeled
    an Integration Key on Pagerduty Service).

    Args:
        routing_key (str): Integration Key from Pagerduty Service

        event_title (str): Title of the Incident

        source (str): Source of the Incident

        severity (str): Severity of the Incident.  Must be one of 'critical',
            'warning', 'error' or 'info'

        details (dict[str, Any]): Additional details to include in the Incident

    Returns:
        None, but triggers the Incident in Pagerduty

    """
    if severity not in ("critical", "error", "info", "warning"):
        raise ValueError(
            "Please select one of 'critical', 'warning', 'error' or 'info' for severity"
        )

    payload = {
        "routing_key": routing_key,
        "event_action": "trigger",
        # "dedup_key": "",
        "payload": {
            "summary": event_title,
            "source": source,
            "severity": severity,
            "custom_details": details,
        },
    }

    response = requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json=payload,
    )
    print(response.json())

    if response.json()["status"] == "success":
        print("Incident Created")
    else:
        print(response.text)  # print error message if not successful


error1 = "REST API /game_types Endpoint Error"
error2 = "tester mctesterson4"

details = {"report_name": "big fat report", "username": "tester mctesty"}
# 'critical', 'warning', 'error' or 'info'
trigger_incident(
    routing_key=os.environ.get("ROUTING_KEY"),
    event_title=error1,
    source="rest-api-prod",
    severity="info",
    details=details,
)
