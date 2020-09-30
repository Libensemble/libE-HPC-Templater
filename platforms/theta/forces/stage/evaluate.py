# Primarily so an independent process, separate from a submitted job, can evaluate
#   outputs and contents of a forces run. Necessary since the qsub command
#   succeeds regardless of if the job succeeds. For ECP-CI.

import os
from time import sleep
from forces_support import test_libe_stats, test_ensemble_dir, check_log_exception

sleeptime = 0
limit = 1500

print('Waiting on test completion for up to {} minutes...'.format(limit/60))

exctr_type = os.environ['LIBE_EXECUTOR']

while sleeptime < limit:
    time.sleep(30)
    sleeptime += 30
    assert sleeptime < limit, "Expected files or environment variables not detected."
    if 'LIBE_EVALUATE_ERROR' in os.environ or 'LIBE_EVALUATE_ENSEMBLE' in os.listdir('.')
        print(' done.', end=" ", flush=True)
        break

if 'LIBE_EVALUATE_ERROR' in os.environ:
    error = os.environ['LIBE_EVALUATE_ERROR']
    if error == 'fail_on_sim':
        test_libe_stats('Exception occurred\n')
    elif error == 'fail_on_submit':
        test_libe_stats('Task Failed\n')

if 'LIBE_EVALUATE_ENSEMBLE' in os.listdir('.'):
    with open('LIBE_EVALUATE_ENSEMBLE', 'r') as f:
        [dir, nworkers, sim_max] = f.readlines()
    test_ensemble_dir(dir.strip('\n'), int(nworkers.strip('\n')), int(sim_max.strip('\n'))
