#!/usr/bin/env python
import os
import numpy as np
from forces_simf import run_forces  # Sim func from current dir

{% if mpi_disable_mprobes is defined %}
import mpi4py
mpi4py.rc.recv_mprobe = False
{% endif %}

# Import libEnsemble modules
from libensemble.libE import libE
from libensemble.manager import LoggedException
from libensemble.tools import parse_args, save_libE_output, add_unique_random_streams
from libensemble import logger
from forces_support import test_libe_stats, test_ensemble_dir, check_log_exception

{% if use_balsam1 is defined %}
use_balsam1 = {{ use_balsam1 }}
{% else %}
use_balsam1 = False
{% endif %}

{% if persis_gen is defined %}
PERSIS_GEN = {{ persis_gen }}
{% else %}
PERSIS_GEN = False
{% endif %}

{% if fail_on_submit is defined %}
FAIL_ON_SUBMIT = {{ fail_on_submit }}
{% else %}
FAIL_ON_SUBMIT = False
{% endif %}

if PERSIS_GEN:
    from libensemble.gen_funcs.persistent_uniform_sampling import persistent_uniform as gen_f
    from libensemble.alloc_funcs.start_only_persistent import only_persistent_gens as alloc_f
else:
    from libensemble.gen_funcs.sampling import uniform_random_sample as gen_f
    from libensemble.alloc_funcs.give_sim_work_first import give_sim_work_first as alloc_f


logger.set_level('DEBUG')  # INFO is now default

nworkers, is_master, libE_specs, _ = parse_args()

if is_master:
    print('\nRunning with {} workers\n'.format(nworkers))

if not os.path.isfile('./forces.x'):
    if os.path.isfile('./build_forces.sh'):
        import subprocess
        subprocess.check_call(['./build_forces.sh'])
sim_app = os.path.abspath('./forces.x')

# Create executor and register sim to it.
if use_balsam1:
    from libensemble.executors.balsam_executors import LegacyBalsamMPIExecutor
    exctr = LegacyBalsamMPIExecutor()
else:
    from libensemble.executors.mpi_executor import MPIExecutor
    exctr = MPIExecutor()
exctr.register_app(full_path=sim_app, app_name='forces')

# Note: Attributes such as kill_rate are to control forces tests, this would not be a typical parameter.

# State the objective function, its arguments, output, and necessary parameters (and their sizes)
sim_specs = {'sim_f': run_forces,         # Function whose output is being minimized
             'in': ['x'],                 # Name of input for sim_f
             'out': [('energy', float)],  # Name, type of output from sim_f
             'user': {'keys': ['seed'],
                      {%- if cores is defined %} 'cores': {{ cores }}, {% endif %}
                      'sim_particles': {{ num_sim_particles }},
                      'sim_timesteps': 5,
                      'sim_kill_minutes': 10.0,
                      'particle_variance': 0.2,
                      'kill_rate': 0.5,
                      'fail_on_sim': {%- if fail_on_sim is defined %} True {%- else %} False {%- endif %}}
             }
# end_sim_specs_rst_tag

# State the generating function, its arguments, output, and necessary parameters.
gen_specs = {'gen_f': gen_f,                  # Generator function
             'in': [],                        # Generator input
             'out': [('x', float, (1,))],     # Name, type and size of data produced (must match sim_specs 'in')
             'user': {'lb': np.array([0]),             # Lower bound for random sample array (1D)
                      'ub': np.array([32767]),         # Upper bound for random sample array (1D)
                      'gen_batch_size': 1000,          # How many random samples to generate in one call
                      }
             }

if PERSIS_GEN:
    alloc_specs = {'alloc_f': alloc_f, 'out': [('given_back', bool)]}
else:
    alloc_specs = {'alloc_f': alloc_f,
                   'out': [('allocated', bool)],
                   'user': {'batch_mode': True,    # If true wait for all sims to process before generate more
                            'num_active_gens': 1}  # Only one active generator at a time
                   }

libE_specs['save_every_k_gens'] = 1000  # Save every K steps
libE_specs['sim_dirs_make'] = True      # Separate each sim into a separate directory

if FAIL_ON_SUBMIT:
    try:
        os.remove(sim_app)
    except FileNotFoundError:
        pass

# So exception can be caught for evaluation in log files
if sim_specs['user']['fail_on_sim'] or FAIL_ON_SUBMIT:
    libE_specs['abort_on_exception'] = False
    is_failure = True
else:
    is_failure = False

# Maximum number of simulations
sim_max = {{ sim_max }}
exit_criteria = {'sim_max': sim_max}

# Create a different random number stream for each worker and the manager
persis_info = add_unique_random_streams({}, nworkers + 1)

try:
    H, persis_info, flag = libE(sim_specs, gen_specs, exit_criteria,
                                persis_info=persis_info,
                                alloc_specs=alloc_specs,
                                libE_specs=libE_specs)

except LoggedException:
    if is_master and sim_specs['user']['fail_on_sim']:
        check_log_exception()
        test_libe_stats('Exception occurred\n')
else:
    if is_master:
        save_libE_output(H, persis_info, __file__, nworkers)
        if FAIL_ON_SUBMIT:
            test_libe_stats('Task Failed\n')

        test_ensemble_dir('./ensemble', nworkers, sim_max, is_failure)
