from aiogram.fsm.state import State, StatesGroup


class WorkoutFlow(StatesGroup):
    choosing_type = State()
    choosing_week = State()
    entering_actual = State()
    choosing_rpe = State()
    entering_comment = State()
    after_exercise = State()


class RecoveryFlow(StatesGroup):
    sleep_hours = State()
    sleep_quality = State()
    energy = State()
    soreness = State()
    stress = State()
    lower_back_state = State()
    resting_pulse = State()
    comment = State()
