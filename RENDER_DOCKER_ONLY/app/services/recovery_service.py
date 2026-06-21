from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import RecoveryLog, User


def save_recovery(session: Session, user: User, data: dict, session_id: int | None = None) -> RecoveryLog:
    log = RecoveryLog(
        user_id=user.id,
        session_id=session_id,
        sleep_hours=Decimal(str(data.get("sleep_hours"))),
        sleep_quality=int(data.get("sleep_quality")),
        energy=int(data.get("energy")),
        soreness=int(data.get("soreness")),
        stress=int(data.get("stress")),
        lower_back_state=int(data.get("lower_back_state")),
        resting_pulse=int(data.get("resting_pulse")),
        comment=data.get("comment"),
    )
    session.add(log)
    session.commit()
    return log


def recovery_recommendation(data: dict) -> str:
    if float(data.get("sleep_hours", 8)) <= 5 or int(data.get("energy", 5)) <= 2 or int(data.get("lower_back_state", 5)) <= 2:
        return (
            "Сегодня лучше сделать лёгкую тренировку:\n"
            "- оставить технику;\n"
            "- снизить рабочие веса;\n"
            "- не идти в отказ;\n"
            "- RPE держать в районе 6–7."
        )
    return "Восстановление выглядит нормально. Можно тренироваться по плану, без геройства."
