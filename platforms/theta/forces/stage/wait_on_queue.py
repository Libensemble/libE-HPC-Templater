import os
import sys
import subprocess
from time import sleep

sleeptime = 0
limit = 3600
queue = sys.argv[1]
user = "csc250stms07"

print('Waiting on {} queue availability for up to {} minutes...'.format(queue, limit/60), flush=True)

while user in subprocess.run('qstat {}'.format(queue).split(), capture_output=True, text=True).stdout.split():
    sleep(60)
    sleeptime += 60
    assert sleeptime < limit, "No availability in {} queue within the time limit.".format(queue)

print(' done.', flush=True)
