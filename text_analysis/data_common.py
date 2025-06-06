from datetime import datetime, timezone

created_now = datetime.now(timezone.utc)

example_reviews = {
    "id": list(range(1, 11)),
    "customer_id": [100, 200, 100, 300, 400, 200, 500, 100, 600, 700],
    "review_text": [
        "this product really sucked, was expensive, and fucking broke on me",
        "i really enjoyed this and i got a great deal!",
        "what a waste of $20, this is bs b!tch",
        "it broken within 5 uses and i couldn't even get a refund! screw this company",
        "absolutely love it — works exactly as advertised. would buy again.",
        "not bad, but the packaging was kinda shit and arrived late",
        "terrible. literally fell apart. don't waste your money.",
        "yo this is dope af, fits perfectly and the quality is 🔥",
        "cheap knockoff. looks like crap and smells like glue. wtf.",
        "quick shipping, great service, no complaints. solid experience.",
    ],
    "created_at": [created_now] * 10,
}
