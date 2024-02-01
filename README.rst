libE-templater
==============

Generate libEnsemble testing environments from templates for a variety of HPC platforms::

    git clone https://github.com/Libensemble/libE-HPC-Templater.git
    cd libE-HPC-Templater; pip install -e .

Installs a ``templater`` utility for generating tests::

    $ templater --help

    Usage: templater [OPTIONS] COMMAND [ARGS]...

        libEnsemble Scaling Tests Templater

        Make test-specific adjustments to the .yaml files in libE-
        templater/platforms/PLATFORM/TEST

    Options:
        --help  Show this message and exit.

    Commands:
        check   Check a test directory (or `all`) for passes/fails.
        config  Edit the base settings for a given machine.
        ls      Display all currently supported machines and their tests
        make    Make tests by machine and variant (or `all`).
        submit  Try submitting each of the tests in a directory (or `all`).

Usage
-----

- See all supported machines and their tests::

    $ templater ls

    Supported Machines and Tests:
       - Perlmutter:  gpu_forces, forces, fbpic,
       - Swing:       fbpic,
       - Summit:      warpx, forces,
       - Bridges:     warpx, forces,
       - Bebop:       warpx, forces,

- Modify machine-specific configuration::

    $ templater config summit

    Summit Configuration: /Users/.../libE-templater/platforms/summit/platform.yaml

    ------------------------------------------------------------------------------------------------------

    {'calling': {'nthreads': 4,
                'sim_kill_minutes': 5,
                'warpx_sim_app': "os.environ['HOME'] + "
                                "'/warpx/Bin/main2d.gnu.TPROF.MPI.CUDA.ex'"},
    'submit': {'alloc_flags': 'smt1',
                'conda_env_name': 'libe-gcc',
                'job_name': 'libe_mproc',
                'job_wallclock_minutes': 20,
                'libe_wallclock': 15,
                'project': 'csc314'}}

    Adjust any of the above platform parameters? (Y/N):

- Create tests for a machine::

    $ templater make theta all

    Writing: ./theta_warpx
    --test_mproc_MOM_zero_resource_workers_5w_8n
    --test_mproc_MOM_4w_8n
    --test_mproc_MOM_128w_256n

    Writing: ./theta_forces
    --test_mproc_MOM_4w_8n_fail_sim
    --test_mproc_MOM_4w_8n
    --test_MPI_balsam2_4w_4n
    --test_mproc_MOM_128w_128n
    --test_mproc_MOM_4w_8n_fail_submit

Utility Structure
-----------------

The ``platforms`` directory contains:

- Platform-specific test configs and templates
- Platform-agnostic configs and templates in ``all``.

Each *platform* directory has:
- Test-type specific directories
- Templates for scheduler submission scripts
- A ``platform.yaml`` with universal parameters for that platform

Each *test* directory has:
- A ``stage`` directory containing files to copy into the output test directory
- ``.yaml`` files corresponding to test-variants

Any staged shell-scripts prefixed with **"prepare"** will be run by the templater
in the output directory. This can help copy files into test-variant directories
or adjust permissions on shell scripts.

Adjusting Tests
---------------

Within all ``.yaml`` files:

- ``calling:``: parameters in libEnsemble python-initialization scripts
- ``submit:``: parameters in batch submission scripts

Note the following about ``platform.yaml``:

    1) Parameters don't have to be universal for all tests. For instance, ``"nthreads": 1`` can be included for each WarpX test, but doesn't have to appear in Forces templates.
    2) Parameters can also appear in test-specific configurations. Test configurations will override values from ``platform.yaml``.

New Test Example
----------------

Suppose we want to define a new test ``"particles"``, only for Theta, with ``mpi_128-nodes``
and ``multiprocess_64-nodes`` variants.

1) Place Jinja templates for calling scripts and submission scripts in ``platforms/all``
or ``platforms/theta``.

2) Create a test directory, ``platforms/theta/particles``.

3) Place configuration ``.yaml`` files to populate templates within this new directory.
In this case, they'll be named ``mpi_128-nodes.yaml`` and ``multiprocess_64-nodes.yaml``.
They must contain ``"calling"`` and ``"submit"`` keys matching a ``"template"``
key-value pairs and any number of other key-value pairs.
For example::

    calling:
        sample_parameter: true
        template: my_calling_template.py
    submit:
        another_parameter: 123
        template: my_submission_template.sh

4) (Optional) place files to copy over to the eventual output directory, ``theta_particles``,
within a new directory ``stage`` inside the above test directory.
