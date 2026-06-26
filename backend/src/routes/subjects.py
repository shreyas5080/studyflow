from fastapi import APIRouter, Depends, HTTPException
from src.deps import get_db, get_current_user
from sqlalchemy.orm import Session
from src.models import Subject
from src.schemas import SubjectCreate
from datetime import date

router = APIRouter()


@router.post("/student/{user_id}/subjects")
def add_subjects(
    user_id: int,
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to add a subject for this student"
        )
    if subject.exam_date < date.today():
        raise HTTPException(status_code=422, detail="Exam date is Invalid.")
    new_subject = Subject(
        user_id=user_id,
        subject_name=subject.subject_name,
        exam_date=subject.exam_date,
        difficulty=subject.difficulty,
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return {"message": "Subject added successfully", "subject": new_subject}


@router.get("/student/{user_id}/subjects")
def get_subjects(
    user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access these subjects"
        )
    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == user_id)
        .order_by(Subject.exam_date)
        .all()
    )
    return {"subjects": subjects}


@router.put("/student/{user_id}/subjects/{subject_id}")
def update_subject(
    user_id: int,
    subject_id: int,
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this subject"
        )

    existing_subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id, Subject.user_id == user_id)
        .first()
    )

    if not existing_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    existing_subject.subject_name = subject.subject_name
    existing_subject.exam_date = subject.exam_date
    existing_subject.difficulty = subject.difficulty

    db.commit()
    db.refresh(existing_subject)

    return {"message": "Subject updated successfully", "subject": existing_subject}


@router.get("/student/{user_id}/subjects/{subject_id}")
def get_subject(
    user_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this subject"
        )

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id, Subject.user_id == user_id)
        .first()
    )

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    return {"subject": subject}


@router.delete("/student/{user_id}/subjects/{subject_id}")
def delete_subject(
    user_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to Delete this subject"
        )
    existing_subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id, Subject.user_id == user_id)
        .first()
    )

    if not existing_subject:
        return {"error": "Subject not found"}

    db.delete(existing_subject)
    db.commit()

    return {"message": "Subject deleted successfully"}
