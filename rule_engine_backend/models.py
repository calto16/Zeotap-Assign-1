from pydantic import BaseModel
from typing import List

# Pydantic models
class RuleInput(BaseModel):
    rule_string: str

class EvaluateData(BaseModel):
    data: dict

class CombinedRules(BaseModel):
    rules: List[str]