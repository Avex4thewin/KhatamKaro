import sys
from app import app
from models import db, User

username, new_password = sys.argv[1], sys.argv[2]
with app.app_context():
    u = User.query.filter_by(username=username).first()
    if not u:
        print("No such user")
    else:
        u.set_password(new_password)
        db.session.commit()
        print("Password reset for", username)