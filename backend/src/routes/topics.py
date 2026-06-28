from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.deps import get_current_user, get_db
from src.models import Subject, SyllabusTopic, User
from src.schemas import TopicCreate, TopicUpdate

router = APIRouter()


@router.post(
    "/subjects/{subject_id}/topics",
    response_model=TopicCreate,
    status_code=status.HTTP_201_CREATED,
)
def create_topic(
    subject_id: int,
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id, Subject.user_id == current_user.id)
        .first()
    )
    if not subject:
        raise HTTPException(
            status_code=404, detail="Subject not found or not owned by user"
        )

    new_topic = SyllabusTopic(
        subject_id=subject_id,
        topic_name=topic.topic_name,
        priority_level=topic.priority_level,
        estimated_hours=topic.estimated_hours,
        is_completed=topic.is_completed,
    )
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic


@router.get("/subjects/{subject_id}/topics", response_model=List[TopicCreate])
def get_topics(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id, Subject.user_id == current_user.id)
        .first()
    )
    if not subject:
        raise HTTPException(
            status_code=404, detail="Subject not found or not owned by user"
        )

    topics = (
        db.query(SyllabusTopic).filter(SyllabusTopic.subject_id == subject_id).all()
    )
    return topics


@router.get("/subjects/{subject_id}/topics/{topic_id}", response_model=TopicCreate)
def get_topic(
    subject_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    topic = (
        db.query(SyllabusTopic)
        .join(Subject)
        .filter(
            SyllabusTopic.id == topic_id,
            SyllabusTopic.subject_id == subject_id,
            Subject.user_id == current_user.id,
        )
        .first()
    )
    if not topic:
        raise HTTPException(
            status_code=404, detail="Topic not found or not owned by user"
        )
    return topic


@router.put("/subjects/{subject_id}/topics/{topic_id}", response_model=TopicCreate)
def update_topic(
    subject_id: int,
    topic_id: int,
    topic_update: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    topic = (
        db.query(SyllabusTopic)
        .join(Subject)
        .filter(
            SyllabusTopic.id == topic_id,
            SyllabusTopic.subject_id == subject_id,
            Subject.user_id == current_user.id,
        )
        .first()
    )
    if not topic:
        raise HTTPException(
            status_code=404, detail="Topic not found or not owned by user"
        )

    update_data = topic_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(topic, field, value)

    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/subjects/{subject_id}/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    subject_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    topic = (
        db.query(SyllabusTopic)
        .join(Subject)
        .filter(
            SyllabusTopic.id == topic_id,
            SyllabusTopic.subject_id == subject_id,
            Subject.user_id == current_user.id,
        )
        .first()
    )
    if not topic:
        raise HTTPException(
            status_code=404, detail="Topic not found or not owned by user"
        )

    db.delete(topic)
    db.commit()
    return None
