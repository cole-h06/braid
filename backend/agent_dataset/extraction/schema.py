from pydantic import BaseModel


class Assertion(BaseModel):

    source: str

    entity: str

    attribute: str

    value: str