import math
from datetime import date
from models import db, SubjectXP
from timeutil import today_local, now_local

SHIELD_CAP = 3
SUBJECT_TITLES = [(1, 'Novice'), (3, 'Apprentice'), (5, 'Adept'), (8, 'Expert'), (12, 'Master')]
JOURNEY_TITLES = [(1, 'Traveller'), (3, 'Wayfarer'), (5, 'Pathfinder'), (8, 'Trailblazer'), (12, 'Voyager')]


def level_from_xp(xp):
    return int(math.sqrt(max(xp, 0) / 50)) + 1


def xp_for_level(level):
    return 50 * (level - 1) ** 2


def progress(xp):
    level = level_from_xp(xp)
    floor_xp = xp_for_level(level)
    span = xp_for_level(level + 1) - floor_xp
    into = xp - floor_xp
    return level, int(into / span * 100), into, span


def _title(level, table):
    name = table[0][1]
    for min_level, label in table:
        if level >= min_level:
            name = label
    return name


def calc_xp(task):
    base = 10 + (task.time_required or 30) / 6
    difficulty_mult = 1 + (task.difficulty or 1) * 0.5
    perf = 1.0
    if task.deadline:
        days_early = (task.deadline - today_local()).days
        if days_early >= 1:
            perf = 1.2
        elif days_early < 0:
            perf = 0.8
    return max(1, round(base * difficulty_mult * perf))


def award_completion(user, task):
    events = []
    today = today_local()

    last = user.last_streak_date
    streak = user.current_streak or 0
    if last != today:
        if last is None:
            streak = 1
        else:
            gap = (today - last).days
            if gap == 1:
                streak += 1
            elif gap == 2 and (user.streak_shields or 0) > 0:
                user.streak_shields -= 1
                streak += 1
                events.append('A streak shield saved your streak.')
            else:
                streak = 1
        user.current_streak = streak
        user.last_streak_date = today
        user.best_streak = max(user.best_streak or 0, streak)
        if streak > 1:
            events.append(f'{streak}-day streak.')
        if streak % 7 == 0:
            user.streak_shields = min(SHIELD_CAP, (user.streak_shields or 0) + 1)
            events.append('Seven-day milestone: +1 streak shield.')

    if user.user_type == 'isc' and task.subject_id:
        xp = calc_xp(task)
        task.xp_awarded = xp
        row = SubjectXP.query.filter_by(user_id=user.id, subject_id=task.subject_id).first()
        if not row:
            row = SubjectXP(user_id=user.id, subject_id=task.subject_id, xp=0, best_level=1)
            db.session.add(row)
        row.xp = (row.xp or 0) + xp
        user.xp_total = (user.xp_total or 0) + xp
        events.insert(0, f'+{xp} XP')

        new_level = level_from_xp(row.xp)
        if new_level > (row.best_level or 1):
            row.best_level = new_level
            events.append(f'{task.subject.name}: level {new_level}, {_title(new_level, SUBJECT_TITLES)}.')
            if (user.streak_shields or 0) < SHIELD_CAP:
                user.streak_shields = (user.streak_shields or 0) + 1
                events.append('Level-up reward: +1 streak shield.')

    return events


def revoke_completion(user, task):
    xp = task.xp_awarded or 0
    if xp and task.subject_id:
        row = SubjectXP.query.filter_by(user_id=user.id, subject_id=task.subject_id).first()
        if row:
            row.xp = max(0, (row.xp or 0) - xp)
        user.xp_total = max(0, (user.xp_total or 0) - xp)
    task.xp_awarded = 0


def build_profile(user):
    total = user.xp_total or 0
    level, pct, into, span = progress(total)

    today = today_local()
    last = user.last_streak_date
    streak = user.current_streak or 0
    if last is None:
        streak = 0
    else:
        gap = (today - last).days
        if gap > 2 or (gap == 2 and not (user.streak_shields or 0)):
            streak = 0

    subjects = []
    for r in sorted(SubjectXP.query.filter_by(user_id=user.id).all(), key=lambda r: -(r.xp or 0)):
        lv, p, _, _ = progress(r.xp or 0)
        subjects.append({'name': r.subject.name, 'level': lv, 'pct': p, 'title': _title(lv, SUBJECT_TITLES)})

    return {
        'is_isc': user.user_type == 'isc',
        'level': level, 'pct': pct, 'into': into, 'span': span,
        'title': _title(level, JOURNEY_TITLES),
        'streak': streak,
        'best_streak': user.best_streak or 0,
        'shields': user.streak_shields or 0,
        'done_today': last == today,
        'subjects': subjects,
    }