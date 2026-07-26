from ..extraction.schema import Assertion


def research_agent():

    return [

        Assertion(
            source="research_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            source="research_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
        ),

        Assertion(
            source="research_agent",
            entity="return_shipping",
            attribute="customer_pays",
            value="yes",
        ),
    ]