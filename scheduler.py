from datetime import date, timedelta
from models import db, Task, FixedCommitment, ScheduledSlot, OneOffCommitment, User

TOTAL_SLOTS_PER_DAY = 48
RECOMPUTE_WINDOW_DAYS = 7


def get_free_slots(user_id, target_date):
    """Return a list of slot numbers (0-47) that are free on this date."""
    day_of_week = target_date.weekday()
    occupied = set()

    user = User.query.get(user_id)
    if user.sleep_start_slot is not None and user.sleep_end_slot is not None:
        for slot in range(user.sleep_start_slot, user.sleep_end_slot):
            occupied.add(slot)

    fixed = FixedCommitment.query.filter_by(user_id=user_id, day_of_week=day_of_week).all()
    for f in fixed:
        occupied.add(f.slot_number)

    one_off = OneOffCommitment.query.filter_by(user_id=user_id, date=target_date).all()
    for o in one_off:
        occupied.add(o.slot_number)

    scheduled = ScheduledSlot.query.filter_by(user_id=user_id, date=target_date).all()
    for s in scheduled:
        occupied.add(s.slot_number)

    return [slot for slot in range(TOTAL_SLOTS_PER_DAY) if slot not in occupied]


def slots_to_minutes(num_slots):
    return num_slots * 30


def minutes_to_slots(minutes):
    """Round up - a task needing 40 minutes still needs 2 full half-hour slots."""
    return int((minutes + 29) // 30)


def buffered_time(task):
    """Apply difficulty time buffer."""
    base = task.time_required or 30
    difficulty = task.difficulty or 1
    return base * (1 + difficulty * 0.1)


def find_consecutive_free_block(free_slots, slots_needed):
    """Find the first run of consecutive free slot numbers at least slots_needed long.
    Returns the starting slot, or None if no such block exists."""
    free_set = set(free_slots)
    for start in sorted(free_slots):
        if all((start + i) in free_set for i in range(slots_needed)):
            return start
    return None


def place_task(task, user_id, search_start_date, search_days):
    """Try to place a task (or its split chunks) somewhere in the next search_days days.
    All-or-nothing: either every chunk gets placed, or none do."""
    chunk_minutes = buffered_time(task) / task.split_count
    chunk_slots = minutes_to_slots(chunk_minutes)

    planned_placements = []
    current_date = search_start_date

    for _ in range(search_days):
        if len(planned_placements) >= task.split_count:
            break

        free = get_free_slots(user_id, current_date)
        start_slot = find_consecutive_free_block(free, chunk_slots)

        if start_slot is not None:
            planned_placements.append((current_date, start_slot))

        current_date += timedelta(days=1)

    if len(planned_placements) < task.split_count:
        return False

    for placement_date, start_slot in planned_placements:
        for i in range(chunk_slots):
            slot = ScheduledSlot(
                task_id=task.id,
                user_id=user_id,
                date=placement_date,
                slot_number=start_slot + i,
                locked=False
            )
            db.session.add(slot)

    db.session.commit()
    return True


def run_scheduler(user_id):
    """Main entry point. Call this after adding/editing/completing a task."""
    today = date.today()
    recompute_cutoff = today + timedelta(days=RECOMPUTE_WINDOW_DAYS)

    ScheduledSlot.query.filter(
        ScheduledSlot.user_id == user_id,
        ScheduledSlot.date >= today,
        ScheduledSlot.date <= recompute_cutoff,
        ScheduledSlot.locked == False
    ).delete()
    db.session.commit()

    all_pending = Task.query.filter_by(user_id=user_id, completed=False).all()

    near_deadline_tasks = [t for t in all_pending if t.deadline and t.deadline <= recompute_cutoff]
    far_or_no_deadline_tasks = [t for t in all_pending if not t.deadline or t.deadline > recompute_cutoff]

    near_deadline_tasks.sort(key=lambda t: (t.deadline, buffered_time(t)))
    far_or_no_deadline_tasks.sort(key=lambda t: (t.deadline or date.max, buffered_time(t)))

    unfit_tasks = []

    for task in near_deadline_tasks:
        days_available = (task.deadline - today).days + 1
        days_available = min(days_available, RECOMPUTE_WINDOW_DAYS)
        success = place_task(task, user_id, today, days_available)
        if not success:
            unfit_tasks.append(task)

    append_start = recompute_cutoff + timedelta(days=1)
    for task in far_or_no_deadline_tasks:
        already_scheduled = ScheduledSlot.query.filter_by(task_id=task.id).first()
        if already_scheduled:
            continue
        success = place_task(task, user_id, append_start, 60)
        if not success:
            unfit_tasks.append(task)

    return unfit_tasks