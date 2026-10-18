import os
from sqlalchemy.pool import NullPool

basedir = os.path.abspath(os.path.dirname(__file__))

# Vercel sets this variable automatically on its servers, so it tells us "we're in production".
IS_PROD = bool(os.environ.get('VERCEL'))

db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

secret = os.environ.get('SECRET_KEY')
if IS_PROD and not secret:
    raise RuntimeError('SECRET_KEY must be set in production')


class Config:
    SECRET_KEY = secret or 'dev-secret-key-change-later'
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = IS_PROD
    SESSION_COOKIE_SAMESITE = 'Lax'
    if db_url:
        SQLALCHEMY_ENGINE_OPTIONS = {'poolclass': NullPool}