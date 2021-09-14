#!/bin/bash -x
#BSUB -P {{ project }}
#BSUB -J {{ job_name }}
#BSUB -W {{ job_wallclock_minutes }}
#BSUB -nnodes {{ num_nodes }}
#BSUB -alloc_flags {{ alloc_flags }}

# Script to launch libEnsemble using multiprocessing

# Name of calling script-
export EXE={{ test }}

# Number of workers.
export NUM_WORKERS={{ num_workers }}

# Wallclock for libE. Slightly smaller than job wallclock
export LIBE_WALLCLOCK={{ libe_wallclock }}

# Name of Conda environment
export CONDA_ENV_NAME={{ conda_env_name }}

export LIBE_PLOTS={{ do_plots }}   # Require plot scripts (see at end)
export PLOT_DIR={{ plot_dir }}

# Need these if not already loaded
# module load python
# module load gcc/4.8.5

module unload xalt

# Activate conda environment
export PYTHONNOUSERSITE=1
. activate $CONDA_ENV_NAME

# hash -d python # Check pick up python in conda env
hash -r # Check no commands hashed (pip/python...)

echo -e "LSB_HOSTS is $LSB_HOSTS"

echo -e "LSB_MCPU_HOSTS is $LSB_MCPU_HOSTS"

python $EXE --comms local --nworkers $NUM_WORKERS > out.txt 2>&1
