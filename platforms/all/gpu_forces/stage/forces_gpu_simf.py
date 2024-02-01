import numpy as np

# Optional status codes to display in libE_stats.txt for each gen or sim
from libensemble.message_numbers import TASK_FAILED, WORKER_DONE


def run_forces(H, persis_info, sim_specs, libE_info):
    """Launches the forces MPI app and auto-assigns ranks and GPU resources.

    Assigns one MPI rank to each GPU assigned to the worker.
    """

    calc_status = 0

    # Parse out num particles, from generator function
    particles = str(int(H["x"][0][0]))

    # app arguments: num particles, timesteps, also using num particles as seed
    args = particles + " " + str(10) + " " + particles

    # Retrieve our MPI Executor
    exctr = libE_info["executor"]

    app_type = "forces"
    if sim_specs["user"]["variant"] == "MULTIAPP":
        app_type = H["app_type"][0].decode()

    if sim_specs["user"]["variant"] == "BASE":
        task = exctr.submit(
            app_name=app_type,
            app_args=args,
            auto_assign_gpus=True,
            match_procs_to_gpus=True,
        )
    else:
        task = exctr.submit(app_name=app_type, app_args=args)

    # Block until the task finishes
    task.wait()

    # Optional - prints GPU assignment (method and numbers)
    check_gpu_setting(task, assert_setting=False, print_setting=True)

    # Try loading final energy reading, set the sim's status
    statfile = "forces.stat"
    try:
        data = np.loadtxt(statfile)
        final_energy = data[-1]
        calc_status = WORKER_DONE
    except Exception:
        final_energy = np.nan
        calc_status = TASK_FAILED

    # Define our output array, populate with energy reading
    output = np.zeros(1, dtype=sim_specs["out"])
    output["energy"] = final_energy

    # Return final information to worker, for reporting to manager
    return output, persis_info, calc_status
