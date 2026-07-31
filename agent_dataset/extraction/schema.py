from datetime import datetime

from pydantic import BaseModel, field_validator


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


class Evidence(BaseModel):

    assertion_id: str

    observed_at: datetime

    provenance_ids: tuple[str, ...]

    cited_source_ids: tuple[str, ...] = ()

    parent_assertion_ids: tuple[str, ...] = ()

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
