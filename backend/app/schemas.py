from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class OptionCreate(BaseModel):
    text: str
    sort_order: int = 0


class QuestionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    required: bool = True
    sort_order: int = 0
    options: List[OptionCreate]


class SurveyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "draft"
    link_template: Optional[str] = None
    questions: List[QuestionCreate] = Field(default_factory=list)


class OptionOut(BaseModel):
    id: int
    text: str
    sort_order: int

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    required: bool
    sort_order: int
    options: List[OptionOut]

    class Config:
        from_attributes = True


class SurveyOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    link_template: Optional[str] = None
    created_at: datetime
    questions: List[QuestionOut] = []

    class Config:
        from_attributes = True


class PublicSurveyOut(SurveyOut):
    submitted: bool = False


class SurveyListOut(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SubmitAnswer(BaseModel):
    question_id: int
    option_id: Optional[int] = None
    option_text: Optional[str] = None


class SubmitPayload(BaseModel):
    answers: List[SubmitAnswer]


class SubmissionOut(BaseModel):
    id: int
    survey_id: int
    public_token: str
    real_id: str
    submitted_at: datetime

    class Config:
        from_attributes = True


class StatsOption(BaseModel):
    option_id: int
    text: str
    count: int
    ratio: float


class StatsQuestion(BaseModel):
    question_id: int
    title: str
    total: int
    options: List[StatsOption]


class StatsOut(BaseModel):
    survey_id: int
    questions: List[StatsQuestion]


class LoginPayload(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    token: str
