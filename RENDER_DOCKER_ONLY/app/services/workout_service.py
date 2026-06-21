import json
import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.workout_plan import WORKOUT_TYPES, get_workout_plan
from app.models import User, WorkoutExerciseLog, WorkoutSession


TYPE_BY_TITLE = {title: key for key, title in WORKOUT_TYPES.items()}


def get_or_create_user(session: Session, tg_user) -> User:
    user = session.scalar(select(User).where(User.telegram_id == tg_user.id))
    if user:
        user.username = tg_user.username
        user.first_name = tg_user.first_name
    else:
        user = User(telegram_id=tg_user.id, username=tg_user.username, first_name=tg_user.first_name)
        session.add(user)
    session.commit()
    return user


def create_workout_session(session: Session, user: User, workout_type: str, cycle_week: int) -> WorkoutSession:
    active = session.scalar(
        select(WorkoutSession).where(WorkoutSession.user_id == user.id, WorkoutSession.status == "active")
    )
    if active:
        active.status = "cancelled"
        active.finished_at = datetime.utcnow()
    workout = WorkoutSession(user_id=user.id, workout_type=workout_type, cycle_week=cycle_week, status="active")
    session.add(workout)
    session.commit()
    return workout


def get_active_session(session: Session, user_id: int) -> WorkoutSession | None:
    return session.scalar(select(WorkoutSession).where(WorkoutSession.user_id == user_id, WorkoutSession.status == "active"))


def parse_actual_value(value: str) -> dict:
    text = value.strip().lower().replace("кг.", "кг")
    weight = None
    weight_match = re.search(r"([+-]?\d+(?:[.,]\d+)?)\s*кг", text)
    if weight_match and "без веса" not in text:
        weight = Decimal(weight_match.group(1).replace(",", "."))

    reps = [int(item) for item in re.findall(r"(?<!\d)(\d+)(?=\s*(?:,|$|сек|раз))", text)]
    if "подход" in text and not reps:
        sets_match = re.search(r"(\d+)\s*подход", text)
        sets_count = int(sets_match.group(1)) if sets_match else None
    else:
        sets_count = len(reps) if reps else None

    return {
        "weight": weight,
        "sets_count": sets_count,
        "reps_json": json.dumps(reps, ensure_ascii=False) if reps else None,
    }


def add_exercise_log(
    session: Session,
    workout_session_id: int,
    exercise: dict,
    actual_value: str,
    rpe: int | None,
    comment: str | None,
    status: str = "completed",
) -> WorkoutExerciseLog:
    parsed = parse_actual_value(actual_value)
    tag = comment if comment in {"Всё ок", "Тяжело", "Боль / дискомфорт", "Техника плохая"} else None
    free_comment = None if comment in {None, "Всё ок", "Пропустить комментарий"} else comment
    log = WorkoutExerciseLog(
        session_id=workout_session_id,
        exercise_name=exercise["name"],
        planned_value=exercise["plan"],
        actual_value=actual_value,
        weight=parsed["weight"],
        sets_count=parsed["sets_count"],
        reps_json=parsed["reps_json"],
        rpe=rpe,
        feedback_tag=tag,
        comment=free_comment,
        status=status,
    )
    session.add(log)
    session.commit()
    return log


def finish_workout(session: Session, workout_session_id: int, general_feedback: str | None = None) -> WorkoutSession:
    workout = session.get(WorkoutSession, workout_session_id)
    workout.status = "completed"
    workout.finished_at = datetime.utcnow()
    workout.general_feedback = general_feedback
    session.commit()
    return workout


def exercise_recommendation(log: WorkoutExerciseLog) -> str:
    if log.feedback_tag == "Боль / дискомфорт":
        return f"{log.exercise_name}: была боль/дискомфорт — снизить нагрузку и не идти в отказ."
    if log.rpe is None:
        return f"{log.exercise_name}: нет RPE — оставить нагрузку."
    if log.rpe <= 7:
        return f"{log.exercise_name}: RPE {log.rpe} — можно повышать нагрузку."
    if log.rpe == 8:
        return f"{log.exercise_name}: RPE 8 — вес оставить."
    return f"{log.exercise_name}: RPE {log.rpe} — не повышать, повторить или снизить нагрузку."


def workout_summary(session: Session, workout_session_id: int) -> str:
    logs = session.scalars(select(WorkoutExerciseLog).where(WorkoutExerciseLog.session_id == workout_session_id)).all()
    lines = ["Итог по нагрузке:"]
    lines.extend(exercise_recommendation(log) for log in logs if log.status == "completed")
    return "\n".join(lines)


def plan_for_state(workout_type: str, cycle_week: int) -> list[dict[str, str]]:
    return get_workout_plan(workout_type, cycle_week)
