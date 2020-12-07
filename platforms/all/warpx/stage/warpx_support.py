import os


def test_ensemble_log_zrw():
    with open('ensemble.log', 'r') as el:
        out = el.readlines()
    assert 'something' in out, \
    print('Pass. ensemble.log correctly contains something.')


def test_ensemble_dir(dir, nworkers, sim_max):
    assert os.path.isdir(dir), 'Specified ensemble directory {} not found.'.format(dir)

    sim_dirs = os.listdir(dir)
    assert all([i.startswith('sim') for i in sim_dirs]), \
        "All directories within ensemble dir not labeled as (or aren't) sim_dirs."

    assert len(sim_dirs) == sim_max, \
        "Number of simulation specific-directories ({}) doesn't match sim_max ({})".format(len(sim_dirs), sim_max)

    print('Pass. Output directory {} contains expected files and structure.'.format(dir))
