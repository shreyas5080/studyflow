from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Boolean,
    ForeignKey,
    Enum,
    TIMESTAMP,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    password_hash = Column(Text, nullable=False)

    full_name = Column(String(100))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    subjects = relationship("Subject", back_populates="user")

    study_plans = relationship("StudyPlan", back_populates="user")

    progress = relationship("Progress", back_populates="user")

    recommendations = relationship("AIRecommendation", back_populates="user")
    ai_table = relationship("AITable", back_populates="user", uselist=False)


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    subject_name = Column(String(100), nullable=False)

    exam_date = Column(Date)

    difficulty = Column(Enum("easy", "medium", "hard", name="Hardness"))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="subjects")

    topics = relationship("SyllabusTopic", back_populates="subject")


class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"

    id = Column(Integer, primary_key=True, index=True)

    subject_id = Column(Integer, ForeignKey("subjects.id"))

    topic_name = Column(String(255), nullable=False)

    priority_level = Column(Enum("low", "medium", "high", name="priority"))

    estimated_hours = Column(Integer)

    is_completed = Column(Boolean, default=False)

    # Relationships
    subject = relationship("Subject", back_populates="topics")

    questions = relationship("ImportantQuestion", back_populates="topic")

    resources = relationship("Resource", back_populates="topic")

    study_sessions = relationship("StudySession", back_populates="topic")

    progress = relationship("Progress", back_populates="topic")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String(100))

    start_date = Column(Date)

    end_date = Column(Date)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="study_plans")

    sessions = relationship("StudySession", back_populates="study_plan")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)

    study_plan_id = Column(Integer, ForeignKey("study_plans.id"))

    topic_id = Column(Integer, ForeignKey("syllabus_topics.id"))

    study_date = Column(Date)

    duration_minutes = Column(Integer)

    status = Column(Enum("pending", "completed", "missed", name="status_type"))

    # Relationships
    study_plan = relationship("StudyPlan", back_populates="sessions")

    topic = relationship("SyllabusTopic", back_populates="study_sessions")


class ImportantQuestion(Base):
    __tablename__ = "important_questions"

    id = Column(Integer, primary_key=True, index=True)

    topic_id = Column(Integer, ForeignKey("syllabus_topics.id"))

    question_text = Column(Text, nullable=False)

    importance_score = Column(Integer)

    source = Column(String(255))

    # Relationships
    topic = relationship("SyllabusTopic", back_populates="questions")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)

    topic_id = Column(Integer, ForeignKey("syllabus_topics.id"))

    resource_type = Column(Enum("youtube", "article", "pdf", "course", name="resource"))

    title = Column(String(255))

    url = Column(Text)

    # Relationships
    topic = relationship("SyllabusTopic", back_populates="resources")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    topic_id = Column(Integer, ForeignKey("syllabus_topics.id"))

    completion_percentage = Column(Integer, default=0)

    last_studied = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="progress")

    topic = relationship("SyllabusTopic", back_populates="progress")


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    recommendation = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="recommendations")


class AITable(Base):
    __tablename__ = "ai_table"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    ai_table = Column(Text)

    user = relationship("User", back_populates="ai_table")
