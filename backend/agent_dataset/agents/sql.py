from ..extraction.schema import Assertion


def sql_agent():

    return [

        Assertion(
            source="sql_agent",
            entity="refund_policy",
            attribute="window_days",
            value="30",
        ),

        Assertion(
            source="sql_agent",
            entity="warranty",
            attribute="length_years",
            value="2",
        ),

        Assertion(
            source="sql_agent",
            entity="customer",
            attribute="tier",
            value="gold",
        ),
    ]