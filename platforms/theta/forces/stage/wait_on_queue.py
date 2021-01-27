import os
import subprocess
from time import sleep

sleeptime = 0
limit = 3600
queue = os.environ['TEST_QUEUE']
user = "csc250stms07"

def check_queue_output():
    return subprocess.run('qstat {}'.format(queue).split(), capture_output=True, text=True).stdout.split()

def user_in_queue(user):
    return user in check_queue_output()

def count_used_nodes():
    return sum([int(i) for i in check_queue_output() if len(i) == 1])

if __name__ == '__main__':

    print('Waiting on {} queue availability for up to {} minutes...'.format(queue, limit/60), flush=True)

    while user_in_queue(user) or count_used_nodes() >= 11:
        sleep(60)
        sleeptime += 60
        assert sleeptime < limit, "No availability in {} queue within the time limit.".format(queue)

    print(' done.', flush=True)
