from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import RecoveryLog, User, WorkoutExerciseLog, WorkoutSession


def stats_text(session: Session, user: User) -> str:
    now = datetime.utcnow()
    base = select(WorkoutSession).where(WorkoutSession.user_id == user.id, WorkoutSession.status == "completed")
    sessions = session.scalars(base).all()
    session_ids = [item.id for item in sessions]
    avg_rpe = None
    if session_ids:
        avg_rpe = session.scalar(select(func.avg(WorkoutExerciseLog.rpe)).where(WorkoutExerciseLog.session_id.in_(session_ids)))
    avg_sleep = session.scalar(select(func.avg(RecoveryLog.sleep_hours)).where(RecoveryLog.user_id == user.id))
    avg_energy = session.scalar(select(func.avg(RecoveryLog.energy)).where(RecoveryLog.user_id == user.id))
    last = max(sessions, key=lambda item: item.started_at, default=None)

    lines = [
        f"Тренировок всего: {len(sessions)}",
        f"За последние 7 дней: {len([item for item in sessions if item.started_at and item.started_at >= now - timedelta(days=7)])}",
        f"За последние 30 дней: {len([item for item in sessions if item.started_at and item.started_at >= now - timedelta(days=30)])}",
        "",
        f"Средний RPE: {round(float(avg_rpe), 1) if avg_rpe else 'нет данных'}",
        f"Средний сон: {round(float(avg_sleep), 1) if avg_sleep else 'нет данных'} часов",
        f"Средняя энергия: {round(float(avg_energy), 1) if avg_energy else 'нет данных'}/5",
    ]
    if last:
        lines.extend(["", "Последняя тренировка:", f"{last.started_at:%Y-%m-%d} — {last.workout_type}, неделя {last.cycle_week}"])
    return "\n".join(lines)
