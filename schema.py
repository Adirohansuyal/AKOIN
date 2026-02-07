from pydantic import BaseModel
from typing import List

class Field(BaseModel):
    code: str
    label: str
    value: float
    source_rule: str

class COREPOutput(BaseModel):
    template: str
    fields: List[Field]
    missing_data: List[str]
    validation_flags: List[str]
