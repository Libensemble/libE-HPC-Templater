# Primarily so an independent process, separate from a submitted job, can evaluate
#   outputs and contents of a forces run. Necessary since the qsub command
#   succeeds regardless of if the job succeeds. For ECP-CI.

import os
import glob
from time import sleep
from forces_support import test_libe_stats, test_ensemble_dir, check_log_exception

sleeptime = 0
limit = 1500

print('Waiting on test completion for up to {} minutes...'.format(limit/60))

# Wait for env vars or files set by conclusion of run_libe_forces
while sleeptime < limit:
    time.sleep(30)
    sleeptime += 30
    assert sleeptime < limit, "Expected output not detected by the time limit."
    if 'LIBE_EVALUATE_ERROR' in os.environ or 'LIBE_EVALUATE_ENSEMBLE' in os.listdir('.')
        print(' done.', end=" ", flush=True)
        break

# If using Balsam, change to job-specific dir. Hopefully only one.
if os.environ.get('BALSAM_DB_PATH'):
    os.chdir(glob.glob(os.environ['BALSAM_DB_PATH'] + '/data/libe_workflow/job_run_libe_forces_*')[0])

# Evaluate output files based on type of error (if any)
if 'LIBE_EVALUATE_ERROR' in os.environ:
    error = os.environ['LIBE_EVALUATE_ERROR']
    if error == 'fail_on_sim':
        test_libe_stats('Exception occurred\n')
    elif error == 'fail_on_submit':
        test_libe_stats('Task Failed\n')

# Evaluate ensemble directory
if 'LIBE_EVALUATE_ENSEMBLE' in os.listdir('.'):
    with open('LIBE_EVALUATE_ENSEMBLE', 'r') as f:
        [dir, nworkers, sim_max] = f.readlines()
    test_ensemble_dir(dir.strip('\n'), int(nworkers.strip('\n')), int(sim_max.strip('\n'))
