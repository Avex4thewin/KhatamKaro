from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Task, Subject, Chapter, FixedCommitment, OneOffCommitment, ScheduledSlot
from forms import SignupForm, LoginForm, TaskForm, OnboardingForm, FixedCommitmentForm, OneOffCommitmentForm, SleepForm
from scheduler import run_scheduler
from flask_migrate import Migrate
from datetime import date, timedelta
from sqlalchemy import case

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username = form.username.data).first()
        if existing_user:
            flash('That username is already taken.')
            return redirect(url_for('signup'))

        new_user = User(username = form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.class_level is None:
                return redirect(url_for('onboarding'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    sort_by = request.args.get('sort', 'deadline')

    query = Task.query.filter_by(user_id=current_user.id)

    if sort_by == 'subject':
        query = query.outerjoin(Subject, Task.subject_id == Subject.id).order_by(
            case((Task.subject_id != None, Subject.name), else_=Task.custom_subject)
        )
    elif sort_by == 'chapter':
        query = query.outerjoin(Chapter, Task.chapter_id == Chapter.id).order_by(
            case((Task.chapter_id != None, Chapter.name), else_=Task.custom_chapter)
        )
    elif sort_by == 'task_type':
        query = query.order_by(Task.task_type)
    elif sort_by == 'difficulty':
        query = query.order_by(Task.difficulty)
    elif sort_by == 'time_required':
        query = query.order_by(Task.time_required)
    else:
        query = query.order_by(Task.deadline)

    tasks = query.all()

    pending_tasks = [t for t in tasks if not t.completed]
    completed_count = len([t for t in tasks if t.completed])
    due_soon_count = len([t for t in pending_tasks if t.deadline and (t.deadline - date.today()).days <= 3])
    next_task = min(pending_tasks, key=lambda t: t.deadline or date.max) if pending_tasks else None

    return render_template('dashboard.html', tasks=tasks, current_sort=sort_by,
                            pending_count=len(pending_tasks),
                            completed_count=completed_count,
                            due_soon_count=due_soon_count,
                            next_task=next_task)

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    form.subject_id.choices = [(0, '-- Select --')] + [(s.id, s.name) for s in current_user.subjects]
    form.chapter_id.choices = [(0, '-- None --')] + [(c.id, c.name) for c in Chapter.query.filter(
        Chapter.subject_id.in_([s.id for s in current_user.subjects])).all()]

    chapter_map = {}
    for s in current_user.subjects:
        chapters = Chapter.query.filter_by(subject_id=s.id, class_level=current_user.class_level).all()
        chapter_map[s.id] = [{'id': c.id, 'name': c.name} for c in s.chapters]

    print("=== ROUTE HIT ===")
    print("Method:", request.method)

    if request.method == 'POST':
        print("Form data received:", request.form)
        print("validate_on_submit result:", form.validate_on_submit())
        print("Form errors:", form.errors)

    if form.validate_on_submit():
        print(">>> VALIDATION PASSED, creating task")
        subject_id = form.subject_id.data if form.subject_id.data != 0 else None
        chapter_id = form.chapter_id.data if form.chapter_id.data != 0 else None

        if not subject_id and not form.custom_subject.data:
            flash('Please select a subject or type your own.')
            return render_template('task_form.html', form=form, title='New Task', chapter_map=chapter_map)

        task = Task(
            subject_id=subject_id,
            chapter_id=chapter_id,
            custom_subject=form.custom_subject.data or None,
            custom_chapter=form.custom_chapter.data or None,
            tasktype=form.tasktype.data,
            deadline=form.deadline.data,
            difficulty=int(form.difficulty.data),
            time_required=form.time_required.data,
            split_count = form.split_count.data or 1,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        unfit = run_scheduler(current_user.id)
        if unfit:
            names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
            flash(f"Warning: could not schedule: {names}")
        else:
            flash('Task added and scheduled!')

        return redirect(url_for('dashboard'))

    return render_template('task_form.html', form=form, title='New Task', chapter_map=chapter_map)

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("You don't have permission to edit that task.")
        return redirect(url_for('dashboard'))

    form = TaskForm(obj=task)
    form.subject_id.choices = [(0, '-- Select --')] + [(s.id, s.name) for s in current_user.subjects]
    form.chapter_id.choices = [(0, '-- None --')] + [(c.id, c.name) for c in Chapter.query.filter(
        Chapter.subject_id.in_([s.id for s in current_user.subjects]),
        Chapter.class_level == current_user.class_level
        ).all()]

    chapter_map = {}
    for s in current_user.subjects:
        chapter_map[s.id] = [{'id': c.id, 'name': c.name} for c in s.chapters]

    if request.method == 'GET':
        form.subject_id.data = task.subject_id or 0
        form.chapter_id.data = task.chapter_id or 0

    if form.validate_on_submit():
        subject_id = form.subject_id.data if form.subject_id.data != 0 else None
        chapter_id = form.chapter_id.data if form.chapter_id.data != 0 else None

        if not subject_id and not form.custom_subject.data:
            flash('Please select a subject or type your own.')
            return render_template('task_form.html', form=form, title='Edit Task', chapter_map=chapter_map)

        task.subject_id = subject_id
        task.chapter_id = chapter_id
        task.custom_subject = form.custom_subject.data or None
        task.custom_chapter = form.custom_chapter.data or None
        task.tasktype = form.tasktype.data
        task.deadline = form.deadline.data
        task.difficulty = int(form.difficulty.data)
        task.time_required = form.time_required.data
        task.split_count = form.split_count.data or 1
        db.session.commit()

        unfit = run_scheduler(current_user.id)
        if unfit:
            names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
            flash(f"Warning: Task updated, but could not schedule: {names}")
        else:
            flash('Task updated and rescheduled!')

        return redirect(url_for('dashboard'))

    return render_template('task_form.html', form=form, title='Edit Task', chapter_map=chapter_map)

@app.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)


    if task.user_id != current_user.id:
        flash("You don't have permission to modify that task.")
        return redirect(url_for('dashboard'))

    task.completed = not task.completed
    db.session.commit()
    unfit = run_scheduler(current_user.id)
    if unfit:
        names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
        flash(f"Warning: could not schedule: {names}")
    else:
        flash('Task added and scheduled!')

    return redirect(url_for('dashboard'))


@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("You don't have permission to delete that task.")
        return redirect(url_for('dashboard'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.')
    return redirect(url_for('dashboard'))           

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    form = OnboardingForm()
    form.subjects.choices = [(s.id, s.name) for s in Subject.query.order_by(Subject.name).all()]

    if form.validate_on_submit():
        if not form.subjects.data:
            flash('Please select at least one subject.')
            return render_template('onboarding.html', form=form)    

        current_user.class_level = int(form.class_level.data)

        selected_subjects = Subject.query.filter(Subject.id.in_(form.subjects.data)).all()
        current_user.subjects = selected_subjects

        db.session.commit()
        flash('Setup complete!')
        return redirect(url_for('dashboard'))

    return render_template('onboarding.html', form=form)               

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def time_to_slot(t):
    return (t.hour * 2) + (1 if t.minute >= 30 else 0)

def time_to_slot_end(t):
    total_minutes = t.hour * 60 + t.minute
    return (total_minutes + 29) // 30

def deadline_urgency_class(deadline):
    if not deadline:
        return 'text-gray-400'
    days_left = (deadline - date.today()).days
    if days_left < 0:
        return 'text-red-400 font-semibold'
    elif days_left == 0:
        return 'text-red-400 font-semibold'
    elif days_left <= 3:
        return 'text-amber-400'
    elif days_left <= 7:
        return 'text-gray-200'
    else:
        return 'text-gray-400'


app.jinja_env.globals.update(deadline_urgency_class=deadline_urgency_class)


@app.route('/commitments', methods=['GET', 'POST'])
@login_required
def commitments():
    fixed_form = FixedCommitmentForm()
    oneoff_form = OneOffCommitmentForm()
    oneoff_form.subject_id.choices = [(0, '-- None --')] + [(s.id, s.name) for s in current_user.subjects]

    if fixed_form.submit_fixed.data and fixed_form.validate_on_submit():
        if not fixed_form.days.data:
            flash('Please select at least one day.')
            return render_template('commitments.html', fixed_form=fixed_form, oneoff_form=oneoff_form,
                                    commitments=get_grouped_commitments(), oneoffs=get_grouped_oneoffs())

        start_slot = time_to_slot(fixed_form.start_time.data)
        end_slot = time_to_slot_end(fixed_form.end_time.data)

        if end_slot <= start_slot:
            flash('End time must be after start time.')
            return render_template('commitments.html', fixed_form=fixed_form, oneoff_form=oneoff_form,
                                    commitments=get_grouped_commitments(), oneoffs=get_grouped_oneoffs())

        for day_str in fixed_form.days.data:
            day = int(day_str)
            for slot in range(start_slot, end_slot):
                entry = FixedCommitment(
                    user_id=current_user.id,
                    day_of_week=day,
                    slot_number=slot,
                    label=fixed_form.label.data
                )
                db.session.add(entry)

        db.session.commit()
        unfit = run_scheduler(current_user.id)
        if unfit:
            names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
            flash(f"Warning: Commitment added but could not schedule: {names}")
        else:
            flash('Commitment added!')

        return redirect(url_for('commitments'))

    if oneoff_form.submit_oneoff.data and oneoff_form.validate_on_submit():
        start_slot = time_to_slot(oneoff_form.start_time.data)
        end_slot = time_to_slot_end(oneoff_form.end_time.data)

        if end_slot <= start_slot:
            flash('End time must be after start time.')
            return render_template('commitments.html', fixed_form=fixed_form, oneoff_form=oneoff_form,
                                    commitments=get_grouped_commitments(), oneoffs=get_grouped_oneoffs())

        subject_id = oneoff_form.subject_id.data if oneoff_form.subject_id.data != 0 else None

        for slot in range(start_slot, end_slot):
            entry = OneOffCommitment(
                user_id=current_user.id,
                date=oneoff_form.date.data,
                slot_number=slot,
                label=oneoff_form.label.data,
                subject_id=subject_id
            )
            db.session.add(entry)

        db.session.commit()
        unfit = run_scheduler(current_user.id)
        if unfit:
            names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
            flash(f"Warning: Commitment added but could not schedule: {names}")
        else:
            flash('One-off commitment added!')

        return redirect(url_for('commitments'))


    sleep_form = SleepForm()
    if current_user.sleep_start_slot is not None:
        sleep_form.start_time.data = None  # TimeField pre-fill from slot number needs a small helper, see below

    if sleep_form.submit_sleep.data and sleep_form.validate_on_submit():
        current_user.sleep_start_slot = time_to_slot(sleep_form.start_time.data)
        current_user.sleep_end_slot = time_to_slot_end(sleep_form.end_time.data)
        db.session.commit()

        unfit = run_scheduler(current_user.id)
        if unfit:
            names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
            flash(f"Warning: Sleep Schedule saved but could not schedule: {names}")
        else:
            flash('Sleep schedule saved!')

        return redirect(url_for('commitments'))

    return render_template('commitments.html', fixed_form=fixed_form, oneoff_form=oneoff_form,sleep_form= sleep_form,
                            commitments=get_grouped_commitments(), oneoffs=get_grouped_oneoffs())


def get_grouped_oneoffs():
    all_oneoffs = OneOffCommitment.query.filter_by(user_id=current_user.id).order_by(
        OneOffCommitment.date, OneOffCommitment.slot_number).all()

    groups = {}
    for o in all_oneoffs:
        key = (o.date, o.label)
        if key not in groups:
            groups[key] = {'date': o.date, 'label': o.label, 'subject': o.subject, 'slots': []}
        groups[key]['slots'].append(o.slot_number)

    result = []
    for key, group in groups.items():
        slots = sorted(group['slots'])
        result.append({
            'date': group['date'],
            'label': group['label'],
            'subject': group['subject'],
            'start_slot': slots[0],
            'end_slot': slots[-1] + 1,
        })

    result.sort(key=lambda g: (g['date'], g['start_slot']))
    return result


def get_grouped_commitments():
    all_commitments = FixedCommitment.query.filter_by(user_id=current_user.id).order_by(
        FixedCommitment.day_of_week, FixedCommitment.slot_number).all()

    groups = {}
    for c in all_commitments:
        key = (c.day_of_week, c.label)
        if key not in groups:
            groups[key] = {'day_of_week': c.day_of_week, 'label': c.label, 'slots': []}
        groups[key]['slots'].append(c.slot_number)

    result = []
    for key, group in groups.items():
        slots = sorted(group['slots'])
        start_slot = slots[0]
        end_slot = slots[-1] + 1
        result.append({
            'day_of_week': group['day_of_week'],
            'label': group['label'],
            'start_slot': start_slot,
            'end_slot': end_slot,
        })

    result.sort(key=lambda g: (g['day_of_week'], g['start_slot']))
    return result


@app.route('/commitments/<int:commitment_id>/delete', methods=['POST'])
@login_required
def delete_commitment(commitment_id):
    commitment = FixedCommitment.query.get_or_404(commitment_id)
    if commitment.user_id != current_user.id:
        flash("You don't have permission to delete that.")
        return redirect(url_for('commitments'))

    db.session.delete(commitment)
    db.session.commit()

    unfit = run_scheduler(current_user.id)
    if unfit:
        names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
        flash(f"Warning: Commitment deleted but could not schedule: {names}")
    else:
        flash('Commitment deleted.')

    return redirect(url_for('commitments'))


@app.route('/commitments/oneoff/delete', methods=['POST'])
@login_required
def delete_oneoff_group():
    date_str = request.form.get('date')
    label = request.form.get('label')
    oneoff_date = date.fromisoformat(date_str)

    OneOffCommitment.query.filter_by(
        user_id=current_user.id,
        date=oneoff_date,
        label=label
    ).delete()
    db.session.commit()

    unfit = run_scheduler(current_user.id)
    if unfit:
        names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
        flash(f"Warning: Commitment deleted but could not schedule: {names}")
    else:
        flash('Commitment deleted.')

    return redirect(url_for('commitments'))

@app.route('/commitments/delete-group', methods=['POST'])
@login_required
def delete_commitment_group():
    day_of_week = int(request.form.get('day_of_week'))
    label = request.form.get('label')

    FixedCommitment.query.filter_by(
        user_id=current_user.id,
        day_of_week=day_of_week,
        label=label
    ).delete()
    db.session.commit()

    unfit = run_scheduler(current_user.id)
    if unfit:
        names = ', '.join([t.subject.name if t.subject else t.custom_subject for t in unfit])
        flash(f"Warning: Commitment deleted but could not schedule: {names}")
    else:
        flash('Commitment deleted.')

    return redirect(url_for('commitments'))


@app.route('/calendar')
@app.route('/calendar/<int:week_offset>')
@login_required
def calendar(week_offset=0):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    user = User.query.get(current_user.id)
    Visible_Slot_Start = user.sleep_end_slot if user.sleep_end_slot is not None else 0
    Visible_Slot_End = 48

    raw_grid = {}
    for slot in range(48):
        raw_grid[slot] = {}
        for day_index in range(7):
            raw_grid[slot][day_index] = None

    for day_index, day_date in enumerate(week_dates):
        day_of_week = day_date.weekday()

        fixed = FixedCommitment.query.filter_by(user_id=current_user.id, day_of_week=day_of_week).all()
        for f in fixed:
            raw_grid[f.slot_number][day_index] = {'label': f.label, 'type': 'fixed'}

        scheduled = ScheduledSlot.query.filter_by(user_id=current_user.id, date=day_date).all()
        for s in scheduled:
            task = s.task
            display_name = task.subject.name if task.subject else task.custom_subject
            chapter_name = task.chapter.name if task.chapter else (task.custom_chapter or '—')
            raw_grid[s.slot_number][day_index] = {
                'label': display_name, 
                'type': 'task',
                'task_id': task.id,
                'chapter': chapter_name,
                'deadline': str(task.deadline) if task.deadline else 'No deadline',
                'difficulty': task.difficulty,
                'time_required': task.time_required,
                'completed': task.completed,}

        one_off = OneOffCommitment.query.filter_by(user_id=current_user.id, date=day_date).all()
        for o in one_off:
            raw_grid[o.slot_number][day_index] = {'label': o.label, 'type': 'oneoff'}

    # Build render grid: merge consecutive identical cells per day into spans
    render_grid = {}
    skip = set()
    for day_index in range(7):
        slot = Visible_Slot_Start
        while slot < Visible_Slot_End:
            if (slot, day_index) in skip:
                slot += 1
                continue
            cell = raw_grid[slot][day_index]
            if cell is None:
                render_grid[(slot, day_index)] = None
                slot += 1
                continue
            span = 1
            while (slot + span < Visible_Slot_End and raw_grid[slot + span][day_index] is not None
                   and raw_grid[slot + span][day_index]['label'] == cell['label']
                   and raw_grid[slot + span][day_index]['type'] == cell['type']):
                skip.add((slot + span, day_index))
                span += 1
            render_grid[(slot, day_index)] = {**cell, 'span': span}
            slot += 1

    return render_template('calendar.html', render_grid=render_grid, week_dates=week_dates,
                            week_offset=week_offset, today=today,
                            visible_start=Visible_Slot_Start, visible_end=Visible_Slot_End)


if __name__== '__main__':
    app.run(debug=True)