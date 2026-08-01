from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SourceMetadata(BaseModel):

    source_id: str

    display_name: str

    owner_id: str | None = None


class Assertion(BaseModel):

    assertion_id: str

    source_id: str

    entity: str

    attribute: str

    value: str


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


class Evidence(BaseModel):

    assertion_id: str

    observed_at: datetime

    provenance_ids: tuple[str, ...] | None

    cited_source_ids: tuple[str, ...] | None = None

    parent_assertion_ids: tuple[str, ...] | None = None

    retrievals: tuple[Retrieval, ...] = Field(
        default=(),
        exclude_if=lambda value: not value,
    )

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(
        cls,
        value,
    ):

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")

        return value


class AgentResult(BaseModel):

    assertions: tuple[Assertion, ...]

    evidence: tuple[Evidence, ...]
