from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .db import Base


class Survey(Base):
    __tablename__ = "surveys"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship(
        "Question", back_populates="survey", cascade="all, delete-orphan", order_by="Question.sort_order"
    )
    tokens = relationship("DistributionToken", back_populates="survey", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="survey", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(String(500), nullable=True)
    required = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    survey = relationship("Survey", back_populates="questions")
    options = relationship(
        "Option", back_populates="question", cascade="all, delete-orphan", order_by="Option.sort_order"
    )
    answers = relationship("Answer", back_populates="question")


class Option(Base):
    __tablename__ = "options"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)

    question = relationship("Question", back_populates="options")


class DistributionToken(Base):
    __tablename__ = "distribution_tokens"
    __table_args__ = (
        UniqueConstraint("survey_id", "public_token", name="uq_survey_token"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    real_id = Column(String(128), nullable=False)
    public_token = Column(String(128), nullable=False)
    submitted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    survey = relationship("Survey", back_populates="tokens")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    public_token = Column(String(128), nullable=False)
    real_id = Column(String(128), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    ip = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)

    survey = relationship("Survey", back_populates="submissions")
    answers = relationship("Answer", back_populates="submission", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("options.id"), nullable=True)
    option_text = Column(String(255), nullable=True)

    submission = relationship("Submission", back_populates="answers")
    question = relationship("Question", back_populates="answers")
