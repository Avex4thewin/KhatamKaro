from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

user_subjects = db.Table('user_subjects',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class User (UserMixin, db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(10), nullable=True)  # 'isc' or 'general'
    xp_total = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    last_streak_date = db.Column(db.Date, nullable=True)
    streak_shields = db.Column(db.Integer, default=0)
    class_level = db.Column(db.Integer, nullable=True)  # 11 or 12
    sleep_start_slot = db.Column(db.Integer, nullable=True)
    sleep_end_slot = db.Column(db.Integer, nullable=True)

    tasks = db.relationship('Task', backref='Owner', lazy=True)
    subjects = db.relationship('Subject', secondary=user_subjects, backref='students', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=True)
    custom_subject = db.Column(db.String(100), nullable=True)
    custom_chapter = db.Column(db.String(150), nullable=True)
    tasktype = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    difficulty = db.Column(db.Integer)  # e.g. 1-5
    time_required = db.Column(db.Integer)  # in minutes
    xp_awarded = db.Column(db.Integer, default=0)
    split_count = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    subject = db.relationship('Subject')
    chapter = db.relationship('Chapter')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    chapters = db.relationship('Chapter', backref='subject', lazy=True)


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    default_difficulty = db.Column(db.Integer, nullable=True)
    class_level = db.Column(db.Integer, nullable=True)  # 11 or 12

    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

class FixedCommitment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday ... 6=Sunday
    slot_number = db.Column(db.Integer, nullable=False)  # 0-47, each = one half-hour block
    label = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=True)  # hex, e.g. "#38BDF8"

class OneOffCommitment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    slot_number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    color = db.Column(db.String(7), nullable=True)  # hex, e.g. "#38BDF8"

    subject = db.relationship('Subject')

class ScheduledSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    slot_number = db.Column(db.Integer, nullable=False)
    locked = db.Column(db.Boolean, default=False)

    task = db.relationship('Task', backref=db.backref('scheduled_slots', cascade='all, delete-orphan'))

class SubjectXP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    xp = db.Column(db.Integer, default=0)
    best_level = db.Column(db.Integer, default=1)

    subject = db.relationship('Subject')
    __table_args__ = (db.UniqueConstraint('user_id', 'subject_id'),)