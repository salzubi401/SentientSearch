from typing import Any, Coroutine, List, Optional

from pydantic import BaseModel, Field, field_validator


class DenseEncoder(BaseModel):
    name: str
    score_threshold: Optional[float] = None
    type: str = Field(default="base")

    class Config:
        arbitrary_types_allowed = True

    @field_validator("score_threshold")
    def set_score_threshold(cls, v):
        return float(v) if v is not None else None

    def __call__(self, docs: List[Any]) -> List[List[float]]:
        raise NotImplementedError("Subclasses must implement this method")

    def acall(self, docs: List[Any]) -> Coroutine[Any, Any, List[List[float]]]:
        raise NotImplementedError("Subclasses must implement this method")
