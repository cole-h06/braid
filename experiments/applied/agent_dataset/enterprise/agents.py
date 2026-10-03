from agent_dataset.extraction.schema import AgentResult, Observation, Retrieval

from .retrieve import api_snapshot, document, sql_records


def make_result(source_id, kind, records):

    observations = []

    for index, record in enumerate(records, 1):

        assertion_id = f"{source_id}-{index:03d}"

        observations.append(Observation(
            assertion_id=assertion_id,
            source_id=source_id,
            entity="northstar_returns",
            attribute=record["attribute"],
            value=record["value"],
            observed_at=record["observed_at"],
            source_modified_at=record["source_modified_at"],
            upstream_source_ids=record["upstream_source_ids"],
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
        observations=tuple(observations),
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
    source_modified_at,
    retrieved_at,
):

    handbook_observations = {
        item.attribute: item
        for item in handbook.observations
    }

    vendor_observations = {
        item.attribute: item
        for item in vendor.observations
    }

    parents = (
        handbook_observations["return_window"],
        handbook_observations["warranty"],
        vendor_observations["shipping_fee"],
    )

    observations = []

    for index, parent in enumerate(parents, 1):

        assertion_id = f"research-{index:03d}"

        observations.append(Observation(
            assertion_id=assertion_id,
            source_id="research",
            entity_namespace=parent.entity_namespace,
            entity=parent.entity,
            attribute=parent.attribute,
            value=parent.value,
            observed_at=retrieved_at,
            source_modified_at=source_modified_at,
            upstream_source_ids=(parent.source_id,),
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
        observations=tuple(observations),
    )
