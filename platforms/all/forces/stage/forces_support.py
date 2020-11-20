import os


def check_log_exception():
    with open('ensemble.log', 'r') as el:
        out = el.readlines()
    assert 'forces_simf.ForcesException\n' in out, \
        "ForcesException not received by manager or logged."
    print('Pass. ensemble.log correctly contains forces_simf.ForcesException.')


def test_libe_stats(status):
    with open('libE_stats.txt', 'r') as ls:
        out = ls.readlines()
    assert all([line.endswith(status) for line in out if 'sim' in line]), \
        "Deliberate error status not logged or raised for all sim instances."
    print('Pass. libE_stats.txt correctly contains {} status for each sim instance.'.format(status[:-1]))


def test_ensemble_dir(dir, nworkers, sim_max):
    if not os.path.isdir(dir):
        print('Specified ensemble directory {} not found.'.format(dir))
        return

    sim_dirs = os.listdir(dir)
    assert all([i.startswith('sim') for i in sim_dirs]), \
        "All directories within ensemble dir not labeled as (or aren't) sim_dirs."

    assert len(sim_dirs) == sim_max, \
        "Number of simulation specific-directories ({}) doesn't match sim_max ({})".format(len(sim_dirs), sim_max)

    files_found = []
    for sim_dir in sim_dirs:
        files_found.append('forces.stat' in os.listdir(os.path.join(dir, sim_dir)))

    assert all(files_found), \
        "forces.stat not found in each sim_dir."

    print('Pass. Output directory {} contains expected files and structure.'.format(dir))
