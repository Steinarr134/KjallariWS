from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

scheduler = BackgroundScheduler()
scheduler.start()

def foo():
    print "sdflkjsflkj"

def bar():
    print "bar"


def run_after(func, seconds=0, minutes=0):
    j = scheduler.add_job(func, 'date',
                      run_date=datetime.fromtimestamp(time.time() + seconds + 60*minutes))


J = scheduler.add_job(bar, 'interval', seconds=3)

run_after(foo, seconds=2)
print "Sdfaaaaaa"
a = datetime.date.fromtimestamp(time.time() + 10)
time.sleep(1000)
