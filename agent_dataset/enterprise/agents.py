from agent_dataset.extraction.schema import (
    AgentResult,
    Assertion,
    Evidence,
    Retrieval,
)

from .retrieve import api_snapshot, document, sql_records


def make_result(source_id, kind, records):

    assertions = []
    evidence = []

    for index, record in enumerate(records, 1):

        assertion_id = f"{source_id}-{index:03d}"

        assertions.append(Assertion(
            assertion_id=assertion_id,
            source_id=source_id,
            entity="northstar_returns",
            attribute=record["attribute"],
            value=record["value"],
        ))

        evidence.append(Evidence(
            assertion_id=assertion_id,
            observed_at=record["observed_at"],
            provenance_ids=(record["provenance_id"],),
            cited_source_ids=(),
            parent_assertion_ids=(),
            retrievals=(Retrieval(
                retrieval_id=f"{source_id}-retrieval-{index:03d}",
                kind=kind,
                resource_id=record["resource_id"],
                retrieved_at=record["retrieved_at"],
                fields=record["fields"],
            ),),
        ))

    return AgentResult(
        assertions=tuple(assertions),
        evidence=tuple(evidence),
    )


def handbook_agent(retrieved_at):

    return make_result(
        "handbook",
        "document",
        document("handbook", retrieved_at),
    )


def faq_agent(retrieved_at):

    return make_result(
        "faq",
        "document",
        document("faq", retrieved_at),
    )


def sql_agent(retrieved_at):

    return make_result(
        "sql",
        "sql",
        sql_records(retrieved_at),
    )


def vendor_agent(retrieved_at):

    return make_result(
        "vendor",
        "api",
        api_snapshot(retrieved_at),
    )


def research_agent(
    handbook,
    vendor,
    observed_at,
    retrieved_at,
):

    handbook_assertions = {
        item.attribute: item
        for item in handbook.assertions
    }

    vendor_assertions = {
        item.attribute: item
        for item in vendor.assertions
    }

    handbook_evidence = {
        item.assertion_id: item
        for item in handbook.evidence
    }

    vendor_evidence = {
        item.assertion_id: item
        for item in vendor.evidence
    }

    parents = (
        handbook_assertions["return_window"],
        handbook_assertions["warranty"],
        vendor_assertions["shipping_fee"],
    )

    assertions = []
    evidence = []

    for index, parent in enumerate(parents, 1):

        assertion_id = f"research-{index:03d}"
        parent_result = (
            handbook_evidence
            if parent.source_id == "handbook"
            else vendor_evidence
        )
        parent_evidence = parent_result[parent.assertion_id]

        assertions.append(Assertion(
            assertion_id=assertion_id,
            source_id="research",
            entity=parent.entity,
            attribute=parent.attribute,
            value=parent.value,
        ))

        evidence.append(Evidence(
            assertion_id=assertion_id,
            observed_at=observed_at,
            provenance_ids=parent_evidence.provenance_ids,
            cited_source_ids=(parent.source_id,),
            parent_assertion_ids=(parent.assertion_id,),
            retrievals=(Retrieval(
                retrieval_id=f"research-retrieval-{index:03d}",
                kind="aggregation",
                resource_id=parent.assertion_id,
                retrieved_at=retrieved_at,
                fields={
                    "input_source_id": parent.source_id,
                    "input_assertion_id": parent.assertion_id,
                },
            ),),
        ))

    return AgentResult(
        assertions=tuple(assertions),
        evidence=tuple(evidence),
    )
