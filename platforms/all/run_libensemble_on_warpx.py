#!/usr/bin/env python

"""
This file is part of the suite of scripts to use LibEnsemble on top of WarpX
simulations. It is the entry point script that runs LibEnsemble. Libensemble
then launches WarpX simulations.

Execute locally via the following command:
    python run_libE_on_warpx.py --comms local --nworkers 3
On summit, use the submission script:
    bsub summit_submit_mproc.sh

The number of concurrent evaluations of the objective function will be
nworkers=1 as one worker is for the persistent gen_f.
"""

# Either 'random' or 'aposmm'
generator_type = {{ gen_type }}

{% if mpi_disable_mprobes is defined %}
import mpi4py
mpi4py.rc.recv_mprobe = False
{% endif %}

{% if use_balsam is defined %}
USE_BALSAM = True
{% else %}
USE_BALSAM = False
{% endif %}

{% if zero_resource_workers is defined %}
ZRW = True
{% else %}
ZRW = False
{% endif %}

import sys
import os
import numpy as np
from warpx_simf import run_warpx  # Sim function from current directory

# Import libEnsemble modules
from libensemble.libE import libE
if generator_type == 'random':
    from libensemble.gen_funcs.sampling \
        import uniform_random_sample as gen_f
    from libensemble.alloc_funcs.give_sim_work_first\
        import give_sim_work_first as alloc_f
elif generator_type == 'aposmm':
    import libensemble.gen_funcs
    libensemble.gen_funcs.rc.aposmm_optimizers = 'nlopt'
    from libensemble.gen_funcs.persistent_aposmm import aposmm as gen_f
    from libensemble.alloc_funcs.persistent_aposmm_alloc \
        import persistent_aposmm_alloc as alloc_f
else:
    print("you shouldn' hit that")
    sys.exit()

from libensemble.tools import parse_args, save_libE_output, \
    add_unique_random_streams
from libensemble import libE_logger

if USE_BALSAM:
    from libensemble.executors.balsam_executor import BalsamMPIExecutor
    exctr = BalsamMPIExecutor(central_mode=True{% if zero_resource_workers is defined %}, zero_resource_workers=[{{ zero_resource_workers }}]{% endif %})
else:
    from libensemble.executors.mpi_executor import MPIExecutor
    exctr = MPIExecutor(central_mode=True{% if zero_resource_workers is defined %}, zero_resource_workers=[{{ zero_resource_workers }}]{% endif %})

libE_logger.set_level('DEBUG')

nworkers, is_master, libE_specs, _ = parse_args()

# Set to full path of warp executable
sim_app = os.path.abspath({{ sim_app }})

# Problem dimension. This is the number of input parameters exposed,
# that LibEnsemble will vary in order to minimize a single output parameter.
n = 4

exctr.register_calc(full_path=sim_app, calc_type='sim')

# State the objective function, its arguments, output, and necessary parameters
# (and their sizes). Here, the 'user' field is for the user's (in this case,
# the simulation) convenience. Feel free to use it to pass number of nodes,
# number of ranks per note, time limit per simulation etc.
sim_specs = {
    # Function whose output is being minimized. The parallel WarpX run is
    # launched from run_WarpX.
    'sim_f': run_warpx,
    # Name of input for sim_f, that LibEnsemble is allowed to modify.
    # May be a 1D array.
    'in': ['x'],
    'out': [
        # f is the single float output that LibEnsemble minimizes.
        ('f', float),
        # All parameters below are not used for calculation,
        # just output for convenience.
        # Final relative energy spread.
        ('energy_std', float, (1,)),
        # Final average energy, in MeV.
        ('energy_avg', float, (1,)),
        # Final beam charge.
        ('charge', float, (1,)),
        # Final beam emittance.
        ('emittance', float, (1,)),
        # input parameter: length of first downramp.
        ('ramp_down_1', float, (1,)),
        # input parameter: Length of second downramp.
        ('ramp_down_2', float, (1,)),
        # input parameter: position of the focusing lens.
        ('zlens_1', float, (1,)),
        # Relative stength of the lens (1. is from
        # back-of-the-envelope calculation)
        ('adjust_factor', float, (1,)),
    ],
    'user': {
        # name of input file
        'input_filename': 'inputs',
        # Run timeouts after 3 mins
        'sim_kill_minutes': {{ sim_kill_minutes }},
        # Run parameters
        'OMP_NUM_THREADS': {{ nthreads }},
        {%+ if num_procs is defined %}'num_procs': {{ num_procs }},{% endif %}
        {%+ if num_nodes is defined %}'num_nodes': {{ num_nodes }},{% endif %}
        {%+ if ranks_per_node is defined %}'ranks_per_node': {{ ranks_per_node }},{% endif %}
        {%+ if e_args is defined %}'e_args': {{ e_args }}{% endif %}
    }
}

# State the generating function, its arguments, output,
# and necessary parameters.
if generator_type == 'random':
    # Here, the 'user' field is for the user's (in this case,
    # the RNG) convenience.
    gen_specs = {
        # Generator function. Will randomly generate new sim inputs 'x'.
        'gen_f': gen_f,
        # Generator input. This is a RNG, no need for inputs.
        'in': [],
        'out': [
            # parameters to input into the simulation.
            ('x', float, (n,))
        ],
        'user': {
            # Total max number of sims running concurrently.
            'gen_batch_size': nworkers,
            # Lower bound for the n parameters.
            'lb': np.array([2.e-3, 2.e-3, 0.005, .1]),
            # Upper bound for the n parameters.
            'ub': np.array([2.e-2, 2.e-2, 0.028, 3.]),
        }
    }

    alloc_specs = {
        # Allocator function, decides what a worker should do.
        # We use a LibEnsemble allocator.
        'alloc_f': alloc_f,
        'out': [
            ('allocated', bool)
        ],
        'user': {
            # If true wait for all sims to process before generate more
            'batch_mode': True,
            # Only one active generator at a time
            'num_active_gens': 1
        }
    }

elif generator_type == 'aposmm':
    # Here, the 'user' field is for the user's (in this case,
    # the optimizer) convenience.
    gen_specs = {
        # Generator function. Will randomly generate new sim inputs 'x'.
        'gen_f': gen_f,
        'in': [],
        'out': [
            # parameters to input into the simulation.
            ('x', float, (n,)),
            # x scaled to a unique cube.
            ('x_on_cube', float, (n,)),
            # unique ID of simulation.
            ('sim_id', int),
            # Whether this point is a local minimum.
            ('local_min', bool),
            # whether the point is from a local optimization run
            # or a random sample point.
            ('local_pt', bool)
        ],
        'user': {
            # Number of sims for initial random sampling.
            # Optimizer starts afterwards.
            'initial_sample_size': max(nworkers-1, 1),
            # APOSMM/NLOPT optimization method
            'localopt_method': 'LN_BOBYQA',
            'num_pts_first_pass': nworkers,
            # Relative tolerance of inputs
            'xtol_rel': 1e-3,
            # Absolute tolerance of output 'f'. Determines when
            # local optimization stops.
            'ftol_abs': 3e-8,
            # Lower bound for the n input parameters.
            'lb': np.array([2.e-3, 2.e-3, 0.005, .1]),
            # Upper bound for the n input parameters.
            'ub': np.array([2.e-2, 2.e-2, 0.028, 3.]),
        }
    }

    alloc_specs = {
        # Allocator function, decides what a worker should do.
        # We use a LibEnsemble allocator.
        'alloc_f': alloc_f,
        'out': [('given_back', bool)],
        'user': {}}

else:
    print("you shouldn' hit that")
    sys.exit()

# Save H to file every N simulation evaluations
libE_specs['save_every_k_sims'] = 100
# Sim directory to be copied for each worker
libE_specs['sim_input_dir'] = 'sim'
libE_specs['sim_dirs_make'] = True

sim_max = {{ sim_max }}  # Maximum number of simulations
exit_criteria = {'sim_max': sim_max}  # Exit after running sim_max simulations

# Create a different random number stream for each worker and the manager
persis_info = add_unique_random_streams({}, nworkers + 1)

# Run LibEnsemble, and store results in history array H
H, persis_info, flag = libE(sim_specs, gen_specs, exit_criteria,
                            persis_info, alloc_specs, libE_specs)

# Save results to numpy file
if is_master:
    save_libE_output(H, persis_info, __file__, nworkers)
    if ZRW:
        open('LIBE_ZRW', 'w')
        test_ensemble_log_zrw()
    with open('LIBE_EVALUATE_ENSEMBLE', 'w') as f:
        for i in ['./ensemble', str(nworkers), str(sim_max)]:
            f.write(i + '\n')
    test_ensemble_dir('./ensemble', nworkerse, sim_max)
