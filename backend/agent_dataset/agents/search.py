from ..extraction.schema import Assertion


def search_agent():

    return [

        Assertion(
            source="search_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            source="search_agent",
            entity="shipping",
            attribute="cost",
            value="free",
        ),

        Assertion(
            source="search_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
        ),
    ]