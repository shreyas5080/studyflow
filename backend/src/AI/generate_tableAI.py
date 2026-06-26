import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from src.models import Subject, AITable
from src.deps import get_db, get_current_user
from fastapi import APIRouter
from datetime import date, timedelta
from typing import Any


load_dotenv()

router = APIRouter()

nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv("NVIDIA_API_KEY")
)

today = date.today().isoformat()


@router.post("/student/{user_id}/subjects/generate-table")
def generate_table(
    user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    today = date.today()
    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == user_id, Subject.exam_date > today)
        .order_by(Subject.exam_date)
        .all()
    )

    if not subjects:
        raise HTTPException(status_code=404, detail="no subject found ")

    subjects_data = [
        {
            "subject_name": s.subject_name,
            "exam_date": str(s.exam_date),
            "difficulty": s.difficulty,
        }
        for s in subjects
    ]

    response = nvidia_client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[
            {
                "role": "system",
                "content": """
                    You are an expert study planner.

                    Rules:
                    1. Use the exam_date as the deadline.
                    2. Hard subjects get more study days than medium subjects.
                    3. Medium subjects get more study days than easy subjects.
                    4. Never schedule study sessions after the exam date.
                    5. Never schedule dates in the past.
                    6. Return ONLY valid JSON.
                    7. Do not return explanations.
                """,
            },
            {
                "role": "user",
                "content": f"""
                    Today's date: {today}

                    Create a study timetable for these upcoming exams only.

                    Subjects:
                    {json.dumps(subjects_data)}

                    Rules:
                    - Study date must be before exam_date.
                    - Study date must not be today if exam is today.
                    - Never schedule study on exam_date. Study date must be strictly before exam_date.
                    - Do not create sessions on or after exam_date.
                    - Each subject has its own exam_date.
                    - Use that subject's exam_date only for that subject.
                    - Do not use the last exam date for all subjects.
                    - For Python, study dates must be before Python's exam_date.
                    - For JAVA, study dates must be before JAVA's exam_date.

                    Return ONLY JSON:
                    {{
                      "timetable": [
                        {{
                          "date": "YYYY-MM-DD",
                          "subject": "Math",
                          "task": "Revise chapter 1",
                          "hours": 2
                        }}
                      ]
                    }}
                    """,
            },
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    ai_text = response.choices[0].message.content or ""

    try:
        time_table_data = clean_ai_json(ai_text)
        time_table_data = validate_timetable(time_table_data, subjects, today)
    except Exception as e:
        print("AI timetable failed:", e)
        print("RAW AI:", ai_text)
        time_table_data = generate_fallback_timetable(subjects, today)

    clean_text = json.dumps(time_table_data)

    existing_table = db.query(AITable).filter(AITable.user_id == user_id).first()

    if existing_table:
        existing_table.ai_table = clean_text
        db.commit()
        db.refresh(existing_table)

        return {"message": "Table Updated seccussfully"}

    ai = AITable(user_id=user_id, ai_table=clean_text)
    db.add(ai)
    db.commit()
    db.refresh(ai)

    return {"message": "Table generated seccussfully"}


@router.get("/student/{user_id}/time-table")
def get_time_table(
    user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    table = db.query(AITable).filter(AITable.user_id == user_id).first()

    if not table:
        return {"timetable": None, "message": "No timetable generated yet"}

    return {"timetable": table.ai_table}


def clean_ai_json(ai_text: str):
    ai_text = ai_text.strip()
    ai_text = ai_text.replace("```json", "").replace("```", "").strip()

    start = ai_text.find("{")

    if start == -1:
        raise HTTPException(status_code=500, detail="AI did not return JSON")

    try:
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(ai_text[start:])
        return data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")


def generate_fallback_timetable(subjects, today: date):
    rows = []

    difficulty_days = {
        "easy": 2,
        "medium": 4,
        "hard": 6,
    }

    difficulty_hours = {
        "easy": 1,
        "medium": 2,
        "hard": 3,
    }

    for subject in subjects:
        difficulty = str(subject.difficulty).lower()
        days_needed = difficulty_days.get(difficulty, 3)
        hours = difficulty_hours.get(difficulty, 2)

        available_dates = []
        current = today

        while current < subject.exam_date:
            available_dates.append(current)
            current += timedelta(days=1)

        selected_dates = available_dates[-days_needed:]

        for index, study_date in enumerate(selected_dates, start=1):
            rows.append(
                {
                    "date": study_date.isoformat(),
                    "subject": subject.subject_name,
                    "task": f"Study {subject.subject_name} part {index}",
                    "hours": hours,
                }
            )

    rows.sort(key=lambda x: (x["date"], x["subject"]))

    return {"timetable": rows}


def validate_timetable(data: dict[str, Any], subjects, today: date):
    deadlines = {subject.subject_name: subject.exam_date for subject in subjects}

    timetable = data.get("timetable")

    if not isinstance(timetable, list):
        raise ValueError("AI JSON must contain timetable list")

    clean_rows = []

    for row in timetable:
        subject = row.get("subject")

        if subject not in deadlines:
            raise ValueError(f"Unknown subject: {subject}")

        study_date = date.fromisoformat(str(row.get("date")))
        exam_date = deadlines[subject]

        if study_date < today:
            raise ValueError("Study date is in the past")

        if study_date >= exam_date:
            raise ValueError(f"{subject} scheduled on/after exam date")

        task = str(row.get("task", "")).strip()
        if not task:
            raise ValueError("Missing task")

        hours = float(row.get("hours"))
        if hours <= 0:
            raise ValueError("Invalid hours")

        clean_rows.append(
            {
                "date": study_date.isoformat(),
                "subject": subject,
                "task": task,
                "hours": int(hours) if hours.is_integer() else hours,
            }
        )

    clean_rows.sort(key=lambda x: (x["date"], x["subject"]))
    return {"timetable": clean_rows}
