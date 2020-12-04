# Primarily so an independent process, separate from a submitted job, can evaluate
#   outputs and contents of a warpx run. Necessary since the qsub command
#   succeeds regardless of if the job succeeds. For ECP-CI.

import os
import sys
import glob
from time import sleep
from forces_support import test_libe_stats, test_ensemble_dir, check_log_exception
from wait_on_queue import user_in_queue

sleeptime = 0
limit = 3000
outfiles = ['job_run_libe_test.out']
user = "csc250stms07"

print('Waiting on test completion for up to {} minutes...'.format(limit/60), flush=True)

fail_detected = False
old_lines = 'nothing'

# Wait for env vars or files set by conclusion of run_libe_forces
while not any([f in os.listdir('.') for f in ['LIBE_EVALUATE_ENSEMBLE', 'FAIL_ON_SIM', 'FAIL_ON_SUBMIT']]):
    sleep(20)
    sleeptime += 20
    for i in glob.glob('./*.output') + glob.glob('./*.error') + outfiles:
        if i in os.listdir('.'):
            with open(i, 'r') as f:
                lines = f.readlines()
            if lines != old_lines:
                print(i)
                for line in lines:
                    print(line)
                old_lines = lines
            if 'Traceback (most recent call last):\n' in lines and 'fail' not in os.environ.get('TEST_TYPE').split('_'):
                fail_detected = True

    if fail_detected:
        sys.exit("Exception detected in job output. Aborting.")
    assert sleeptime < limit, "Expected output not detected by the time limit."
    assert user_in_queue(user), "User and job not actually in queue."

print(' done.', end=" ", flush=True)

# Evaluate output files based on type of error (if any)
if 'FAIL_ON_SIM' in os.listdir('.'):
    test_libe_stats('Exception occurred\n')
elif 'FAIL_ON_SUBMIT' in os.listdir('.'):
    test_libe_stats('Task Failed\n')

# Evaluate ensemble directory
if 'LIBE_EVALUATE_ENSEMBLE' in os.listdir('.'):
    with open('LIBE_EVALUATE_ENSEMBLE', 'r') as f:
        [dir, nworkers, sim_max] = f.readlines()
    test_ensemble_dir(dir.strip('\n'), int(nworkers.strip('\n')), int(sim_max.strip('\n')))
