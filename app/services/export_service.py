from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import NutritionLog, RecoveryLog, User, WorkoutExerciseLog, WorkoutSession


def _frames(session: Session, user: User) -> dict[str, pd.DataFrame]:
    sessions = session.scalars(select(WorkoutSession).where(WorkoutSession.user_id == user.id)).all()
    session_ids = [item.id for item in sessions]
    logs = session.scalars(select(WorkoutExerciseLog).where(WorkoutExerciseLog.session_id.in_(session_ids))).all() if session_ids else []
    recovery = session.scalars(select(RecoveryLog).where(RecoveryLog.user_id == user.id)).all()
    nutrition = session.scalars(select(NutritionLog).where(NutritionLog.user_id == user.id)).all()
    by_session = {item.id: item for item in sessions}

    session_df = pd.DataFrame([{
        "session_id": item.id,
        "date": item.started_at.date() if item.started_at else None,
        "workout_type": item.workout_type,
        "cycle_week": item.cycle_week,
        "started_at": item.started_at,
        "finished_at": item.finished_at,
        "status": item.status,
        "general_feedback": item.general_feedback,
    } for item in sessions])

    logs_df = pd.DataFrame([{
        "session_id": item.session_id,
        "date": by_session[item.session_id].started_at.date() if item.session_id in by_session else None,
        "workout_type": by_session[item.session_id].workout_type if item.session_id in by_session else None,
        "cycle_week": by_session[item.session_id].cycle_week if item.session_id in by_session else None,
        "exercise_name": item.exercise_name,
        "planned_value": item.planned_value,
        "actual_value": item.actual_value,
        "weight": float(item.weight) if item.weight is not None else None,
        "sets_count": item.sets_count,
        "reps_json": item.reps_json,
        "rpe": item.rpe,
        "feedback_tag": item.feedback_tag,
        "comment": item.comment,
    } for item in logs])

    recovery_df = pd.DataFrame([{
        "date": item.created_at.date() if item.created_at else None,
        "session_id": item.session_id,
        "sleep_hours": float(item.sleep_hours) if item.sleep_hours is not None else None,
        "sleep_quality": item.sleep_quality,
        "energy": item.energy,
        "soreness": item.soreness,
        "stress": item.stress,
        "lower_back_state": item.lower_back_state,
        "resting_pulse": item.resting_pulse,
        "comment": item.comment,
    } for item in recovery])

    nutrition_df = pd.DataFrame([{
        "date": item.date,
        "calories": item.calories,
        "protein_g": item.protein_g,
        "fat_g": item.fat_g,
        "carbs_g": item.carbs_g,
        "comment": item.comment,
    } for item in nutrition])

    summary = {
        "metric": ["Всего тренировок", "Средний RPE", "Средний сон", "Средняя энергия", "Последняя тренировка"],
        "value": [
            len([item for item in sessions if item.status == "completed"]),
            round(logs_df["rpe"].dropna().mean(), 2) if "rpe" in logs_df else None,
            round(recovery_df["sleep_hours"].dropna().mean(), 2) if "sleep_hours" in recovery_df else None,
            round(recovery_df["energy"].dropna().mean(), 2) if "energy" in recovery_df else None,
            max((item.started_at for item in sessions if item.started_at), default=None),
        ],
    }

    return {
        "Workout_Sessions": session_df,
        "Exercise_Logs": logs_df,
        "Recovery_Control": recovery_df,
        "Nutrition_Logs": nutrition_df,
        "Summary": pd.DataFrame(summary),
    }


def export_all_excel(session: Session, user: User) -> Path:
    frames = _frames(session, user)
    if frames["Workout_Sessions"].empty and frames["Recovery_Control"].empty:
        raise ValueError("Данных пока нет.")
    path = get_settings().export_path / f"training_export_{user.telegram_id}_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, frame in frames.items():
            frame.to_excel(writer, index=False, sheet_name=sheet)
    return path


def export_workouts_csv(session: Session, user: User) -> Path:
    frames = _frames(session, user)
    if frames["Exercise_Logs"].empty:
        raise ValueError("Тренировок пока нет.")
    path = get_settings().export_path / f"workouts_{user.telegram_id}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    frames["Exercise_Logs"].to_csv(path, index=False, encoding="utf-8-sig")
    return path


def export_recovery_csv(session: Session, user: User) -> Path:
    frames = _frames(session, user)
    if frames["Recovery_Control"].empty:
        raise ValueError("Данных восстановления пока нет.")
    path = get_settings().export_path / f"recovery_{user.telegram_id}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    frames["Recovery_Control"].to_csv(path, index=False, encoding="utf-8-sig")
    return path
