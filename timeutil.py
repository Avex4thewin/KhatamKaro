from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Asia/Kolkata')

def now_local():
    return datetime.now(TZ)

def today_local():
    return now_local().date()