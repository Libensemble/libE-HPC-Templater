import os
import subprocess
from time import sleep

sleeptime = 0
limit = 3600
queue = os.environ['TEST_QUEUE']
user = "csc250stms07"

print('Waiting on {} queue availability for up to {} minutes...'.format(queue, limit/60), flush=True)

def user_in_queue(user):
    return user in subprocess.run('qstat {}'.format(queue).split(), capture_output=True, text=True).stdout.split()

while user_in_queue(user):
    sleep(60)
    sleeptime += 60
    assert sleeptime < limit, "No availability in {} queue within the time limit.".format(queue)

print(' done.', flush=True)
