from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

scheduler = BackgroundScheduler()
scheduler.start()


def run_after(func, seconds=0, minutes=0):
    j = scheduler.add_job(func, 'date',
                      run_date=datetime.fromtimestamp(time.time() + seconds + 60*minutes))


def get_status(d):
    status = d.send_and_receive('Status')
    if status is None:
        raise Exception(d.Name + " did not respond when we checked for status")
    else:
        return status
