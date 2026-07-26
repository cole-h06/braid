from ..extraction.schema import Assertion


def document_agent():

    return [

        Assertion(
            source="document_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            source="document_agent",
            entity="shipping",
            attribute="cost",
            value="free",
        ),

        Assertion(
            source="document_agent",
            entity="support",
            attribute="hours",
            value="24/7",
        ),
    ]