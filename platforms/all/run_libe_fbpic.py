import os
import numpy as np
from varying_parameters import varying_parameters
from analysis_script import analyze_simulation

from libensemble.libE import libE
from libensemble.tools import parse_args
from libensemble.tools import save_libE_output, add_unique_random_streams
from libensemble.executors.mpi_executor import MPIExecutor

from libensemble.alloc_funcs.start_only_persistent import only_persistent_gens
from libe_opt.persistent_gp import persistent_gp_mf_disc_gen_f
from libe_opt.sim_functions import run_simulation
from libensemble import logger

logger.set_level('DEBUG')

gen_type = 'bo'
sim_max = {{ sim_max }}
run_async = {{ run_async }}
max_rsets_per_worker = {{max_rsets_per_worker}}  # If None then use range

scheduler_opts = {'match_slots':{{ match_slots }}, 'split2fit':{{ split2fit }}}

USE_CUDA_VISIBLE_DEVICES = {{ cuda_visible_devices }}
MPICH_GPU_SUPPORT = {{ mpich_gpu_support }}

nworkers, is_master, libE_specs, _ = parse_args()
sim_template = 'template_simulation_script.py'

sim_specs={'sim_f': run_simulation,
           'in': ['x', 'resource_sets', 'z'],
           'out': [('f', float),
                   ('energy_med', float, (1,)),
                   ('energy_mad', float, (1,)),
                   ('charge', float, (1,)),
                   ('laser_scale', float, (1,)),
                   ('z_foc', float, (1,)),
                   ('mult', float, (1,)),
                   ('plasma_scale', float, (1,)),
                   ('resolution', float, None)],
           'user': {'var_params': ['laser_scale', 'z_foc', 'mult', 'plasma_scale'],
                    'analysis_func': analyze_simulation,
                    'sim_template': sim_template,
                    'z_name': 'resolution',
                    'USE_CUDA_VISIBLE_DEVICES': USE_CUDA_VISIBLE_DEVICES,
                    'MPICH_GPU_SUPPORT':MPICH_GPU_SUPPORT,
                    }
           }

gen_specs={'gen_f': persistent_gp_mf_disc_gen_f,
           'persis_in': ['x', 'f', 'sim_id', 'z'],
           'out': [('x', float, (4,)),
                   ('resource_sets', int),
                   ('z', float, None)],
           'user': {'gen_batch_size': 8,
                    'lb': np.array([0.7, 3. , 0.6, 0.1]),
                    'ub': np.array([1.05, 7.5 , 0.8 , 1.5 ]),
                    'name': 'resolution',
                    'range': [2.0, 4.0],
                    'discrete': True,
                    'cost_func': lambda z: z[0][0]**3,
                    'max_rsets_per_worker': max_rsets_per_worker
                    }
           }

alloc_specs={'alloc_f': only_persistent_gens,
             'out': [('given_back', bool)],
             'user': {'async_return': run_async}}


libE_specs['sim_dirs_make'] = True
libE_specs['sim_dir_copy_files'] = [sim_template]
# libE_specs['save_every_k_sims'] = 5
libE_specs['dedicated_mode'] = False   # False is default.
libE_specs['zero_resource_workers'] = [1]

exit_criteria = {'sim_max': sim_max}  # Exit after running sim_max simulations


# Setup MPI executor
{% if mpi_runner is defined %}
exctr = MPIExecutor(custom_info={'mpi_runner': '{{ mpi_runner }}' })
{% else %}
exctr = MPIExecutor()
{% endif %}

# Can registesr app even though does not yet exist at this name/path
exctr.register_app(full_path='simulation_script.py', calc_type='sim')

# Create a different random number stream for each worker and the manager
persis_info = add_unique_random_streams({}, nworkers + 1)

# Run LibEnsemble, and store results in history array H
H, persis_info, flag = libE(sim_specs, gen_specs, exit_criteria,
                            persis_info, alloc_specs, libE_specs)

# Save results to numpy file
if is_master:
    save_libE_output(H, persis_info, __file__, nworkers)
