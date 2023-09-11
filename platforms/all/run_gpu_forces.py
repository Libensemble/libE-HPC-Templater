import os
import sys
import argparse

import numpy as np
from forces_gpu_simf import run_forces

from libensemble import Ensemble
from libensemble.alloc_funcs.start_only_persistent import (
    only_persistent_gens as alloc_f,
)
from libensemble.executors import MPIExecutor

from libensemble.gen_funcs.persistent_sampling_var_resources import (
    uniform_sample_diff_simulations,
    uniform_sample_with_var_gpus,
)
from libensemble.gen_funcs.persistent_sampling import persistent_uniform

from libensemble.specs import AllocSpecs, ExitCriteria, GenSpecs, LibeSpecs, SimSpecs


def get_variant():
    parser = argparse.ArgumentParser(prog="run_gpu_...")
    parser.add_argument(
        "--variant",
        type=str,
        nargs="?",
        choices=["multiapp", "varresources", "base"],
        default="base",
    )
    args, misc_args = parser.parse_known_args(sys.argv[1:])
    return args.variant.upper()


def setup_exctr_apps(VARIANT):
    if VARIANT == "MULTIAPP":
        cpu_app = os.path.join(os.getcwd(), "forces_cpu.x")
        if not os.path.isfile(cpu_app):
            sys.exit(f"{cpu_app} not found - please build first")

    gpu_app = os.path.join(os.getcwd(), "forces_gpu.x")
    if not os.path.isfile(gpu_app):
        sys.exit(f"{gpu_app} not found - please build first")

    exctr = MPIExecutor()
    exctr.register_app(full_path=gpu_app, app_name="gpu_app")
    if VARIANT == "MULTIAPP":
        exctr.register_app(full_path=cpu_app, app_name="cpu_app")
    return exctr


def setup_gen_specs(VARIANT, nsim_workers):
    gen_specs = GenSpecs(
        persis_in=["sim_id"],
        outputs=[("x", float, (1,))],
        user={"initial_batch_size": nsim_workers},
    )

    BIG_BOUNDS = {
        "lb": np.array([50000]),
        "ub": np.array([100000]),
    }

    if VARIANT == "MULTIAPP":
        gen_specs.gen_f = uniform_sample_diff_simulations
        gen_specs.outputs.append(
            ("num_procs", int),
            ("num_gpus", int),
            ("app_type", "S10"),
        )
        gen_specs.user["lb"] = np.array([5000])
        gen_specs.user["ub"] = np.array([10000])
        gen_specs.user["max_procs"] = nsim_workers // 2

    elif VARIANT == "VARRESOURCES":
        gen_specs.gen_f = uniform_sample_with_var_gpus
        gen_specs.outputs.append(("num_gpus", int))
        gen_specs.user.update(BIG_BOUNDS)
        gen_specs.user["max_gpus"] = nsim_workers

    else:
        gen_specs.gen_f = persistent_uniform
        gen_specs.user.update(BIG_BOUNDS)
    gen_specs.user["variant"] = VARIANT

    return gen_specs


if __name__ == "__main__":
    VARIANT = get_variant()
    exctr = setup_exctr_apps(VARIANT)

    ensemble = Ensemble(parse_args=True, executor=exctr)
    nsim_workers = ensemble.nworkers - 1

    ensemble.libE_specs = LibeSpecs(
        num_resource_sets=nsim_workers,
        sim_dirs_make=True,
        stats_fmt={"show_resource_sets": True}
        # resource_info = {"gpus_on_node": 4},  # for mocking GPUs
    )

    ensemble.sim_specs = SimSpecs(
        sim_f=run_forces, inputs=["x"], out=[("energy", float)]
    )

    if VARIANT == "MULTIAPP":
        ensemble.sim_specs.inputs.append("app_type")
        ensemble.exit_criteria = ExitCriteria(sim_max=nsim_workers * 2)
    else:
        ensemble.exit_criteria = ExitCriteria(sim_max=8)

    ensemble.gen_specs = setup_gen_specs(VARIANT, nsim_workers)

    ensemble.alloc_specs = AllocSpecs(alloc_f=alloc_f, user={"async_return": False})

    ensemble.add_random_streams()

    ensemble.run()

    if ensemble.is_manager:
        chksum = np.sum(ensemble.H["energy"])
