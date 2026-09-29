from app import app
from models import db, Subject, Chapter, Task, OneOffCommitment, User, user_subjects
import seed as seed_module


def snapshot():
    snap = {'users': {}, 'tasks': {}, 'oneoffs': {}}
    for u in User.query.all():
        snap['users'][u.id] = [s.name for s in u.subjects]
    for t in Task.query.all():
        snap['tasks'][t.id] = (
            t.subject.name if t.subject else None,
            t.chapter.name if t.chapter else None,
            t.chapter.class_level if t.chapter else None,
        )
    for o in OneOffCommitment.query.all():
        snap['oneoffs'][o.id] = o.subject.name if o.subject else None
    return snap


def wipe():
    Task.query.update({Task.subject_id: None, Task.chapter_id: None})
    OneOffCommitment.query.update({OneOffCommitment.subject_id: None})
    db.session.execute(user_subjects.delete())
    Chapter.query.delete()
    Subject.query.delete()
    db.session.commit()


def relink(snap):
    for uid, names in snap['users'].items():
        user = User.query.get(uid)
        user.subjects = Subject.query.filter(Subject.name.in_(names)).all() if names else []

    for tid, (sname, cname, clevel) in snap['tasks'].items():
        task = Task.query.get(tid)
        subj = None
        if sname:
            subj = Subject.query.filter_by(name=sname).first()
            if subj:
                task.subject_id = subj.id
            else:
                task.custom_subject = task.custom_subject or sname
        if cname:
            chapter = None
            if subj:
                chapter = Chapter.query.filter_by(subject_id=subj.id, name=cname, class_level=clevel).first()
                if not chapter:
                    chapter = Chapter.query.filter_by(subject_id=subj.id, name=cname).first()
            if chapter:
                task.chapter_id = chapter.id
            else:
                task.custom_chapter = task.custom_chapter or cname

    for oid, sname in snap['oneoffs'].items():
        if sname:
            subj = Subject.query.filter_by(name=sname).first()
            if subj:
                OneOffCommitment.query.get(oid).subject_id = subj.id

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        snap = snapshot()
        wipe()
        print("Wiped all subjects and chapters.")

    seed_module.seed()

    with app.app_context():
        relink(snap)
        print("Relinked users, tasks and one-off commitments.")