store_records = [
    "Store 1728 - API Key Disabled",
    "Store 1113 - User has been deactivated",
    "Store 1454 - API Key doesn't exist",
    "Store 2134 - Wrong API Region for this API Key",
    "Store 3232 - API Usage Limit Reached for this API Key",
]


def generate_error_explanation(error_reason: str) -> str:
    """
    Helper Function used to generate Error Explanations for
    Failed Integration Syncs

    Args:
        error_reason (str): The Error Reason from the Vendor

    Returns:
        String of the customized Error Explanation for the Failure.
    """
    error_mapping = {
        "API Key Disabled": (
            "The Store has deactivated their API Key.  Please alert "
            "the Store to generate a new API Key or shutdown their Sync"
        ),
        "User has been deactivated": (
            "The Store's Integration Account has been "
            "closed.  Please alert the Store to shutdown their Sync."
        ),
        "API Key doesn't exist": (
            "The Store's API Key doesn't exist.  "
            "Please alert the Store to re-enter their Credentials"
        ),
        "Wrong API Region for this API Key": (
            "The Store's API Region is "
            "incorrect.  Please alert the Store to re-enter their Credentials"
        ),
    }

    return error_mapping.get(
        error_reason,
        "Unknown Error Reason, for a more detailed explanation please reach out to xyz",
    )


for value in store_records:
    store = value.split(" - ")[0]
    error_reason = value.split(" - ")[1]
    explanation = generate_error_explanation(error_reason)
    print(
        f"""{store} Integration Failure\nFailure Reason: {error_reason}\nExplanation: {explanation} """
    )
