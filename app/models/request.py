"""
Request models for Ask ZodiaQ API.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class ZodiaQTopic(str, Enum):
    """The six top-level question cards shown on the Ask ZodiaQ home screen."""
    MARRIAGE          = "marriage"           # When will I get married?
    JOB               = "job"                # When will I get a job?
    HOUSE             = "house"              # When will I buy a house?
    CAREER_BEST       = "career_best"        # Which career is best for me?
    BUSINESS          = "business"           # Should I start my own business?
    GOVERNMENT_JOB    = "government_job"     # Will I get a government job?


class BirthData(BaseModel):
    name: str = Field(..., description="Full name of the person")
    sex: str  = Field(..., description="M or F")
    dob: str  = Field(..., description="Date of birth in DD/MM/YYYY format")
    tob: str  = Field(..., description="Time of birth in HH:MM (24-hour) format")
    lat: float = Field(..., description="Birth latitude")
    lon: float = Field(..., description="Birth longitude")
    timezone: float = Field(5.5, description="Timezone offset from UTC (e.g. 5.5 for IST)")


class ZodiaQRequest(BaseModel):
    """Single-request model: one person, one topic."""
    birth_data: BirthData
    topic: ZodiaQTopic = Field(..., description="Question topic selected by user")
