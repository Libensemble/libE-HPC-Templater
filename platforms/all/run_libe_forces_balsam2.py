#!/usr/bin/env python
import os
import socket
import numpy as np

from libensemble.libE import libE
from libensemble.gen_funcs.sampling import uniform_random_sample
from forces_simf_balsam import run_forces_balsam
from libensemble.executors import BalsamExecutor
from libensemble.tools import parse_args, add_unique_random_streams

from balsam.api import ApplicationDefinition

BALSAM_SITE = '{{ balsam2_site }}'

# Parse number of workers, comms type, etc. from arguments
nworkers, is_manager, libE_specs, _ = parse_args()

# State the sim_f, inputs, outputs
sim_specs = {
    "sim_f": run_forces_balsam,  # sim_f, imported above
    "in": ["x"],  # Name of input for sim_f
    "out": [("energy", float)],  # Name, type of output from sim_f
}

# State the gen_f, inputs, outputs, additional parameters
gen_specs = {
    "gen_f": uniform_random_sample,  # Generator function
    "out": [("x", float, (1,))],  # Name, type and size of data from gen_f
    "user": {
        "lb": np.array([1000]),  # User parameters for the gen_f
        "ub": np.array([3000]),
        "gen_batch_size": 8,
    },
}

# Create and work inside separate per-simulation directories
libE_specs["sim_dirs_make"] = True

# Instruct libEnsemble to exit after this many simulations
exit_criteria = {"sim_max": {{ sim_max }}}

persis_info = add_unique_random_streams({}, nworkers + 1)

apps = ApplicationDefinition.load_by_site(BALSAM_SITE)
RemoteForces = apps["RemoteForces"]

exctr = BalsamExecutor()
exctr.register_app(RemoteForces, app_name="forces")

# Launch libEnsemble
H, persis_info, flag = libE(
    sim_specs, gen_specs, exit_criteria, persis_info=persis_info, libE_specs=libE_specs
)
