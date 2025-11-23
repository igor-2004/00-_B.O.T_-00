from apscheduler.schedulers.background import BackgroundScheduler
import time
from db import get_submissions_last_seconds

sched = None

def cleanup_job():
    # Пример: просто печатаем количество за 24ч
    print("Cleanup job running...")

def start_scheduler():
    global sched
    if sched is not None:
        return
    sched = BackgroundScheduler()
    # Ежечасно
    sched.add_job(cleanup_job, 'interval', hours=1)
    sched.start()
    print("Scheduler started")
