from pydantic import BaseModel, Field
from typing import List


class Anomaly(BaseModel):
    metric: str = Field(
        ..., description="Name of the problematic metric"
    )  # we add metadata to help the LLM
    value: float = Field(..., description="The metric's measured value")
    reason: str = Field(
        ..., description="Explanation of why it's considered problematic"
    )


class Recommendation(BaseModel):
    action: str = Field(
        ..., description="Action to take to improve performance or stability"
    )
    expected_benefit: str = Field(
        ..., description="Reason or expected impact of the action"
    )


class AnalysisResult(BaseModel):
    analysis_summary: str = Field(
        ..., description="Brief summary of overall system health"
    )
    anomalies_detected: List[Anomaly] = Field(
        default_factory=list, description="List of detected anomalies"
    )
    recommendations: List[Recommendation] = Field(
        default_factory=list, description="List of recommendations"
    )
