from datetime import datetime

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class SourceMetadata(BaseModel):

    source_id: str

    display_name: str

    owner_id: str | None = None


class Retrieval(BaseModel):

    retrieval_id: str

    kind: Literal["document", "sql", "api", "aggregation"]

    resource_id: str

    retrieved_at: datetime

    fields: dict[str, str] = Field(default_factory=dict)

    @field_validator("retrieved_at")
    @classmethod
    def validate_retrieved_at(
        cls,
        value,
    ):

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("retrieved_at must be timezone-aware")

        return value


class Observation(BaseModel):
    """A structured assertion accompanied by provenance metadata."""

    assertion_id: str

    source_id: str

    entity_namespace: str = "agent_dataset"

    entity: str

    attribute: str

    value: str

    observed_at: datetime

    source_modified_at: datetime | None = None

    upstream_source_ids: tuple[str, ...] | None = None

    cited_source_ids: tuple[str, ...] | None = None

    parent_assertion_ids: tuple[str, ...] | None = None

    retrievals: tuple[Retrieval, ...] = Field(
        default=(),
        exclude_if=lambda value: not value,
    )

    metadata: dict[str, Any] = Field(default_factory=dict)

    dependency_signals: dict[str, Any] = Field(default_factory=dict)

    @field_validator("observed_at", "source_modified_at")
    @classmethod
    def validate_timestamps(
        cls,
        value,
    ):

        if value is not None and (
            value.tzinfo is None or value.utcoffset() is None
        ):
            raise ValueError("timestamps must be timezone-aware")

        return value


class AgentResult(BaseModel):

    observations: tuple[Observation, ...]
