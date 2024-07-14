from datetime import datetime, timezone

created_now = datetime.now(timezone.utc)

example_reviews = {
    "id": [1, 2, 3, 4],
    "customer_id": [100, 200, 100, 300],
    "review_text": [
        "this product really sucked, was expensive, and fucking broke on me",
        "i really enjoyed this and i got a great deal !",
        "what a waste of $20, this is bs b!tch",
        "it broken within 5 uses and i couldn't even get a refund! screw this company",
    ],
    "created_at": [created_now] * 4,
}
