# Lead Classification Module

This module classifies business leads using OpenAI to determine their quality and fit.

## Usage

```python
from classifier import (
    read_leads_from_file,
    classify_lead,
    classify_all_leads,
    filter_qualified_leads,
    print_classification_report,
    LeadQuality
)

# Read all leads
leads = read_leads_from_file()

# Classify a single lead
classification = classify_lead(leads[0])
print_classification_report(classification)

# Classify all leads
all_classifications = classify_all_leads()

# Filter for qualified leads
qualified = filter_qualified_leads(
    all_classifications,
    require_budget=True,
    require_business_domain=True,
    min_quality=LeadQuality.MEDIUM
)
```

## Classification Criteria

1. **Budget**: Does the lead mention $25,000+ budget?
1. **Domain**: Is the email from a business domain (not gmail, yahoo, etc.)?
1. **Legitimacy**: Is this a genuine inquiry or spam/bogus?

## Running

```bash
# Make sure OPENAI_API_KEY is set
export OPENAI_API_KEY="your-key"

# Run the classifier
python classifier.py
```
