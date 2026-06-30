"""
Lead Classification Module

This module provides functions to classify business leads using OpenAI's API
via the instructor library. Leads are evaluated on:
1. Budget threshold (>$25,000)
2. Email domain reputation (business vs personal/suspicious domains)
3. Overall legitimacy (detecting spam/bogus submissions)
"""

import os
import json
from enum import Enum
from pathlib import Path
from typing import Optional

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field


# --- Enums and Models ---


class LeadQuality(str, Enum):
    """Overall lead quality classification."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SPAM = "spam"


class DomainType(str, Enum):
    """Classification of email domain type."""

    BUSINESS = "business"
    PERSONAL = "personal"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"


class Lead(BaseModel):
    """Input model for a lead."""

    id: str
    name: str
    email: str
    company: str
    message: str
    phone: str = ""


class LeadClassification(BaseModel):
    """Output model for lead classification results."""

    lead_id: str = Field(description="The ID of the lead being classified")

    # Budget analysis
    has_sufficient_budget: bool = Field(
        description="Whether the lead indicates a budget of $25,000 or more"
    )
    estimated_budget: Optional[float] = Field(
        default=None,
        description="Estimated budget amount in USD if mentioned, None if not specified",
    )
    budget_reasoning: str = Field(description="Brief explanation of budget assessment")

    # Domain analysis
    domain_type: DomainType = Field(description="Classification of the email domain")
    domain_reasoning: str = Field(
        description="Brief explanation of domain classification"
    )

    # Legitimacy analysis
    is_legitimate: bool = Field(
        description="Whether the lead appears to be a genuine business inquiry"
    )
    legitimacy_reasoning: str = Field(
        description="Brief explanation of legitimacy assessment"
    )

    # Overall classification
    quality: LeadQuality = Field(description="Overall quality rating of the lead")
    recommendation: str = Field(
        description="Brief recommendation on how to handle this lead"
    )


# --- File I/O Functions ---


def read_leads_from_file(filepath: str | Path | None = None) -> list[Lead]:
    """
    Read leads from the inputs.json file.

    Args:
        filepath: Path to the JSON file. Defaults to inputs.json in the same directory.

    Returns:
        List of Lead objects parsed from the file.
    """
    if filepath is None:
        filepath = Path(__file__).parent / "inputs.json"

    filepath = Path(filepath)

    with open(filepath, "r") as f:
        data = json.load(f)

    return [Lead(**item) for item in data]


def read_single_lead(lead_id: str, filepath: str | Path | None = None) -> Lead | None:
    """
    Read a single lead by ID from the inputs file.

    Args:
        lead_id: The ID of the lead to retrieve.
        filepath: Path to the JSON file.

    Returns:
        Lead object if found, None otherwise.
    """
    leads = read_leads_from_file(filepath)
    for lead in leads:
        if lead.id == lead_id:
            return lead
    return None


# --- Classification Functions ---


def get_instructor_client() -> instructor.Instructor:
    """Create and return an instructor-wrapped OpenAI client."""
    return instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_TEST_KEY")))


def classify_lead(
    lead: Lead, client: instructor.Instructor | None = None
) -> LeadClassification:
    """
    Classify a single lead using OpenAI.

    Args:
        lead: The Lead object to classify.
        client: Optional instructor client. Created if not provided.

    Returns:
        LeadClassification with detailed analysis.
    """
    if client is None:
        client = get_instructor_client()

    system_prompt = """You are a lead qualification expert. Analyze the provided lead 
and classify it based on:

1. BUDGET: Does the lead indicate a budget of $25,000 or more? Look for explicit 
   mentions of budget, project scope, or investment amounts.

2. EMAIL DOMAIN: Classify the email domain:
   - BUSINESS: Professional company domains (e.g., company.com, company.io)
   - PERSONAL: Common free email providers (gmail.com, yahoo.com, hotmail.com, etc.)
   - SUSPICIOUS: Temporary email services, unusual TLDs, or spam-like domains

3. LEGITIMACY: Is this a genuine business inquiry or spam/bogus submission?
   Consider: coherent message, realistic company info, professional tone, 
   reasonable requests.

Provide honest, objective assessments. A lead can have a business domain but still 
be low quality if the message content is poor."""

    user_prompt = f"""Classify this lead:

ID: {lead.id}
Name: {lead.name}
Email: {lead.email}
Company: {lead.company}
Phone: {lead.phone}
Message: {lead.message}"""

    result = client.chat.completions.create(
        model="gpt-5-nano",
        response_model=LeadClassification,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return result


def classify_all_leads(
    leads: list[Lead] | None = None, filepath: str | Path | None = None
) -> list[LeadClassification]:
    """
    Classify all leads from file or provided list.

    Args:
        leads: Optional list of Lead objects. If not provided, reads from file.
        filepath: Path to inputs file if leads not provided.

    Returns:
        List of LeadClassification results.
    """
    if leads is None:
        leads = read_leads_from_file(filepath)

    client = get_instructor_client()
    results = []

    for lead in leads:
        classification = classify_lead(lead, client)
        results.append(classification)

    return results


def filter_qualified_leads(
    classifications: list[LeadClassification],
    require_budget: bool = True,
    require_business_domain: bool = False,
    min_quality: LeadQuality = LeadQuality.MEDIUM,
) -> list[LeadClassification]:
    """
    Filter classifications to find qualified leads.

    Args:
        classifications: List of LeadClassification objects.
        require_budget: Only include leads with budget >= $25,000.
        require_business_domain: Only include leads with business email domains.
        min_quality: Minimum quality level to include.

    Returns:
        Filtered list of qualified lead classifications.
    """
    quality_order = {
        LeadQuality.SPAM: 0,
        LeadQuality.LOW: 1,
        LeadQuality.MEDIUM: 2,
        LeadQuality.HIGH: 3,
    }
    min_quality_score = quality_order[min_quality]

    qualified = []
    for c in classifications:
        # Check quality threshold
        if quality_order[c.quality] < min_quality_score:
            continue

        # Check budget requirement
        if require_budget and not c.has_sufficient_budget:
            continue

        # Check domain requirement
        if require_business_domain and c.domain_type != DomainType.BUSINESS:
            continue

        qualified.append(c)

    return qualified


def print_classification_report(classification: LeadClassification) -> None:
    """Print a formatted report for a single lead classification."""
    print(f"\n{'=' * 60}")
    print(f"Lead ID: {classification.lead_id}")
    print(f"{'=' * 60}")

    print(f"\n  Budget Assessment:")
    print(
        f"    Sufficient (>=$25k): {'Yes' if classification.has_sufficient_budget else 'No'}"
    )
    if classification.estimated_budget:
        print(f"    Estimated Amount: ${classification.estimated_budget:,.2f}")
    print(f"    Reasoning: {classification.budget_reasoning}")

    print(f"\n  Domain Assessment:")
    print(f"    Type: {classification.domain_type.value}")
    print(f"    Reasoning: {classification.domain_reasoning}")

    print(f"\n  Legitimacy Assessment:")
    print(f"    Legitimate: {'Yes' if classification.is_legitimate else 'No'}")
    print(f"    Reasoning: {classification.legitimacy_reasoning}")

    print(f"\n  Overall Classification:")
    print(f"    Quality: {classification.quality.value.upper()}")
    print(f"    Recommendation: {classification.recommendation}")


# --- Main Execution ---

if __name__ == "__main__":
    print("Loading leads from inputs.json...")
    leads = read_leads_from_file()
    print(f"Found {len(leads)} leads\n")

    print("Classifying leads with OpenAI...")
    classifications = classify_all_leads(leads)

    # Print all results
    for classification in classifications:
        print_classification_report(classification)

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    qualified = filter_qualified_leads(
        classifications,
        require_budget=True,
        require_business_domain=True,
        min_quality=LeadQuality.MEDIUM,
    )

    print(f"\nTotal leads processed: {len(classifications)}")
    print(
        f"High quality leads: {sum(1 for c in classifications if c.quality == LeadQuality.HIGH)}"
    )
    print(
        f"Medium quality leads: {sum(1 for c in classifications if c.quality == LeadQuality.MEDIUM)}"
    )
    print(
        f"Low quality leads: {sum(1 for c in classifications if c.quality == LeadQuality.LOW)}"
    )
    print(
        f"Spam leads: {sum(1 for c in classifications if c.quality == LeadQuality.SPAM)}"
    )
    print(
        f"\nQualified leads (budget + business domain + medium+ quality): {len(qualified)}"
    )

    if qualified:
        print("\nQualified lead IDs:")
        for q in qualified:
            print(f"  - {q.lead_id}")
