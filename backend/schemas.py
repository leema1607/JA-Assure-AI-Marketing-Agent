from typing import Literal
from pydantic import BaseModel, Field

Brand = Literal["DoctorShield", "Jade", "Jaguar Transit"]
Platform = Literal["LinkedIn", "Instagram", "X", "Blog", "Reel"]
Language = Literal["English", "Malay", "Bahasa Indonesia", "Thai", "Chinese"]

class WorkflowRequest(BaseModel):
    brand: Brand
    platform: Platform
    objective: str = "Create Content"
    topic: str
    language: Language = "English"

class ReviewRequest(BaseModel):
    content_id: int
    decision: Literal["approve", "edit", "reject"]
    comments: str = ""
    edited_content: str = ""

class FeedbackRequest(BaseModel):
    content_id: int
    reason: str
    details: str = ""

class LeadRequest(BaseModel):
    brand: Brand
    target_industry: str
    location: str = "Malaysia"
    count: int = Field(default=5, ge=1, le=20)

class ComplianceRequest(BaseModel):
    content_id: int
    content: str

class WorkflowResponse(BaseModel):
    content_id: int
    research: str
    content: str
    compliance_status: str
    compliance_issues: list[str]
    status: str
