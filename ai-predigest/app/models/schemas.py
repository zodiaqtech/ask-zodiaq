"""
Pydantic models for API request and response schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class DomainType(str, Enum):
    """Supported astrology domains"""
    MARRIAGE = "Marriage"
    LOVE_LIFE = "Love_Life"
    CHILDREN = "Children"
    PARENTING = "Parenting"
    CAREER = "Career"
    FINANCE = "Finance"
    HEALTH = "Health"
    EDUCATION = "Education"
    FOREIGN = "Foreign"


class MarriageSubtopic(str, Enum):
    """Marriage domain subtopics"""
    MARRIAGE_PROSPECTS = "Marriage Prospects"
    MARITAL_STABILITY = "Marital Stability"


class Person(BaseModel):
    """Person birth details model"""
    name: str = Field(..., description="Person's name")
    sex: Literal["male", "female"] = Field(..., description="Person's gender")
    dob: str = Field(..., description="Date of birth (DD/MM/YYYY)")
    tob: str = Field(..., description="Time of birth (HH:MM)")
    lat: float = Field(..., description="Birth latitude")
    lon: float = Field(..., description="Birth longitude")
    timezone: Optional[float] = Field(default=5.5, description="Timezone offset from UTC (e.g. 5.5 for IST). Defaults to 5.5 (IST).")
    
    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v: str) -> str:
        try:
            parts = v.split('/')
            if len(parts) != 3:
                raise ValueError
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            datetime(year, month, day)
            return v
        except:
            raise ValueError("Date must be in DD/MM/YYYY format")
    
    @field_validator('tob')
    @classmethod
    def validate_tob(cls, v: str) -> str:
        try:
            parts = v.split(':')
            if len(parts) != 2:
                raise ValueError
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            return v
        except:
            raise ValueError("Time must be in HH:MM format (24-hour)")


class SinglePersonRequest(BaseModel):
    """Request model for single person analysis"""
    name: str = Field(..., description="Person's name")
    sex: Literal["male", "female"] = Field(..., description="Person's gender")
    dob: str = Field(..., description="Date of birth (DD/MM/YYYY)")
    tob: str = Field(..., description="Time of birth (HH:MM)")
    lat: float = Field(..., description="Birth latitude")
    lon: float = Field(..., description="Birth longitude")
    domain: str = Field(default="Marriage", description="Astrology domain")
    subtopic: List[str] = Field(default=["Marriage Prospects"], description="Subtopics to analyze")
    language: Literal["Hindi", "English"] = Field(default="Hindi", description="Output language")
    timezone: Optional[float] = Field(default=5.5, description="Timezone offset from UTC (e.g. 5.5 for IST). Defaults to 5.5 (IST).")
    
    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v: str) -> str:
        try:
            parts = v.split('/')
            if len(parts) != 3:
                raise ValueError
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            datetime(year, month, day)
            return v
        except:
            raise ValueError("Date must be in DD/MM/YYYY format")
    
    @field_validator('tob')
    @classmethod
    def validate_tob(cls, v: str) -> str:
        try:
            parts = v.split(':')
            if len(parts) != 2:
                raise ValueError
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            return v
        except:
            raise ValueError("Time must be in HH:MM format (24-hour)")


class TwoPersonRequest(BaseModel):
    """Request model for two-person compatibility analysis"""
    name: str = Field(..., description="First person's name")
    sex: Literal["male", "female"] = Field(..., description="First person's gender")
    dob: str = Field(..., description="Date of birth (DD/MM/YYYY)")
    tob: str = Field(..., description="Time of birth (HH:MM)")
    lat: float = Field(..., description="Birth latitude")
    lon: float = Field(..., description="Birth longitude")
    domain: str = Field(default="Marriage", description="Astrology domain")
    subtopic: List[str] = Field(default=["Marriage Compatibility"], description="Subtopics to analyze")
    person2: Person = Field(..., description="Second person's details")
    language: Literal["Hindi", "English"] = Field(default="Hindi", description="Output language")
    timezone: Optional[float] = Field(default=5.5, description="Timezone offset from UTC (e.g. 5.5 for IST). Defaults to 5.5 (IST).")


class PredictRequest(BaseModel):
    """Unified prediction request supporting both single and two-person analysis"""
    name: str
    sex: Literal["male", "female"]
    dob: str
    tob: str
    lat: float
    lon: float
    domain: str = "Marriage"
    subtopic: List[str] = ["Marriage Prospects"]
    person2: Optional[Person] = None
    language: Literal["Hindi", "English"] = "Hindi"
    timezone: Optional[float] = Field(default=5.5, description="Timezone offset from UTC (e.g. 5.5 for IST). Defaults to 5.5 (IST).")
    
    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v: str) -> str:
        try:
            parts = v.split('/')
            if len(parts) != 3:
                raise ValueError
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            datetime(year, month, day)
            return v
        except:
            raise ValueError("Date must be in DD/MM/YYYY format")
    
    @field_validator('tob')
    @classmethod
    def validate_tob(cls, v: str) -> str:
        try:
            parts = v.split(':')
            if len(parts) != 2:
                raise ValueError
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            return v
        except:
            raise ValueError("Time must be in HH:MM format (24-hour)")


class DateRange(BaseModel):
    """Date range model"""
    start: str
    end: str


class PastEvent(BaseModel):
    """Past event model"""
    title: str
    date_range: DateRange
    possible_outcomes: str
    astrological_reasoning: str
    evidence: str


class DashaEntry(BaseModel):
    """Dasha period entry"""
    dasha_name: str
    date_range: DateRange
    impact: str


class DashaAnalysis(BaseModel):
    """Dasha analysis model"""
    past_6_months: List[DashaEntry]
    next_6_months: List[DashaEntry]


class QuestionAnswer(BaseModel):
    """Question and answer model"""
    question: str
    general_answer: str
    astrological_analysis: str
    summary: Optional[str] = None


class RemedyCategory(BaseModel):
    """Remedy with benefits"""
    description: str
    benefits: List[str]


class Remedies(BaseModel):
    """Remedies model"""
    astrological: List[Any]  # Can be string or RemedyCategory
    general: List[Any]


class ManglikStatus(BaseModel):
    """Manglik dosha status"""
    person1: Optional[bool] = None
    person2: Optional[bool] = None


class TwoPersonAnalysis(BaseModel):
    """Two-person compatibility analysis"""
    overall_score: Optional[float] = None
    relationship_score: Optional[float] = None
    manglik_status: ManglikStatus
    detailed_analysis: Optional[str] = None


class Overview(BaseModel):
    """Response overview"""
    topic: str
    subtopics: List[str]
    summary: Optional[str] = None


class PersonOutput(BaseModel):
    """Person data in response"""
    name: str
    sex: str
    dob: str
    tob: str
    lat: float
    lon: float
    timezone: str = "UTC+5:30"


class PredictionResult(BaseModel):
    """Complete prediction result"""
    response_id: str
    input_id: str
    generated_at: str
    source: str = "ZODIAQ-RAG-v1"
    person: PersonOutput
    person2: Optional[PersonOutput] = None
    is_two_person: bool = False
    overview: Overview
    past_events: List[PastEvent] = []
    dasha_analysis: Optional[DashaAnalysis] = None
    questions: List[Dict[str, Any]] = []
    remedies: Remedies
    two_person_analysis: TwoPersonAnalysis
    ui_hints: Dict[str, Any] = {}


class PredictResponse(BaseModel):
    """Initial predict endpoint response"""
    success: bool
    response_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    message: Optional[str] = None


class StatusResponse(BaseModel):
    """Status endpoint response"""
    success: bool
    response_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: Optional[int] = None
    message: Optional[str] = None
    error_message: Optional[str] = None


class ResultResponse(BaseModel):
    """Result endpoint response"""
    success: bool
    response_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    database: Optional[str] = None


class SSEEvent(BaseModel):
    """Server-Sent Event model"""
    event: str
    data: Dict[str, Any]
