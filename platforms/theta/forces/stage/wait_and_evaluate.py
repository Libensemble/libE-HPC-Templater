# Primarily so an independent process, separate from a submitted job, can evaluate
#   outputs and contents of a forces run. Necessary since the qsub command
#   succeeds regardless of if the job succeeds. For ECP-CI.

import os
import sys
import glob
from time import sleep
from forces_support import test_libe_stats, test_ensemble_dir, check_log_exception
from wait_on_queue import user_in_queue

def get_Balsam_job_dirs():
    return glob.glob(os.environ['BALSAM_DB_PATH'] + '/data/libe_workflow/job_run_libe_forces_*')

def completion_files_detected():
    return any([f in os.listdir('.') for f in ['LIBE_EVALUATE_ENSEMBLE', 'FAIL_ON_SIM', 'FAIL_ON_SUBMIT']])

if __name__ == '__main__':

    sleeptime = 0
    limit = 3000
    outfiles = ['job_run_libe_test.out']
    user = "csc250stms07"

    print('Waiting on test completion for up to {} minutes...'.format(limit/60), flush=True)

    # If using Balsam, change to job-specific dir after waiting. Hopefully only one.
    if os.environ.get('BALSAM_DB_PATH'):
        USE_BALSAM = True
        while not len(get_Balsam_job_dirs()):
            sleep(5)
            sleeptime += 5
            assert sleeptime < limit, "Expected output not detected by the time limit."
        print('Changing to Balsam job directory')
        os.chdir(get_Balsam_job_dirs()[0])
    else:
        USE_BALSAM = False

    fail_detected = False
    old_lines = 'nothing'
    fail_test_case = 'fail' in os.environ.get('TEST_TYPE').split('_')

    # Wait for env vars or files set by conclusion of run_libe_forces
    while not completion_files_detected():
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
                if 'Traceback (most recent call last):\n' in lines and not fail_test_case:
                    fail_detected = True

        if fail_detected:
            sys.exit("Exception detected in job output. Aborting.")
        assert sleeptime < limit, "Expected output not detected by the time limit."
        assert user_in_queue(user), "User and job not actually in queue."

    print(' done.', end=" ", flush=True)

    # Evaluate output files based on type of error (if any)
    if USE_BALSAM:  #  So eval routines run separately from balsam job
        if 'FAIL_ON_SIM' in os.listdir('.'):
            test_libe_stats('Exception occurred\n')
        elif 'FAIL_ON_SUBMIT' in os.listdir('.'):
            test_libe_stats('Task Failed\n')

        # Evaluate ensemble directory
        if 'LIBE_EVALUATE_ENSEMBLE' in os.listdir('.'):
            with open('LIBE_EVALUATE_ENSEMBLE', 'r') as f:
                [dir, nworkers, sim_max] = f.readlines()
            test_ensemble_dir(dir.strip('\n'), int(nworkers.strip('\n')), int(sim_max.strip('\n')), fail_test_case)
