from ..extraction.schema import Assertion


def api_agent():

    return [

        Assertion(
            source="api_agent",
            entity="refund_policy",
            attribute="window_days",
            value="14",
        ),

        Assertion(
            source="api_agent",
            entity="warranty",
            attribute="length_years",
            value="1",
        ),

        Assertion(
            source="api_agent",
            entity="shipping",
            attribute="cost",
            value="5",
        ),
    ]