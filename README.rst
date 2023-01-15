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
        - Swing:   fbpic,
        - Summit:  warpx, forces,
        - Bridges: warpx, forces,
        - Bebop:   warpx, forces,
        - Cori:    forces,
        - Theta:   warpx, forces,

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

- Submit one (or more) tests to the scheduler::

    COMING SOON

- Check the results of completed tests::

    COMING SOON

Utility Structure
-----------------

The ``platforms`` directory contains platform-specific test configurations
and templates in directories named after each platform and platform-agnostic
configurations and templates in ``all``. Each of these directories contains
sub-directories, templates, and configurations for each supported test. For example,
``platforms/bebop`` contains ``forces`` and ``warpx`` directories that match both supported tests,
two different templates for submission scripts (used by both tests), and ``platform.yaml``,
containing parameters universal to tests on that platform.

As an example, ``platforms/bebop/forces`` contains both a ``stage`` directory
and multiple ``.yaml`` files. Each ``.yaml`` file corresponds to a variant of ``forces``,
with different numbers of nodes, comm-types, etc. that can be tested on ``bebop``.
``stage`` contains files to be copied to the output test-directory ``bebop_forces``.::

    /platforms
        /bebop
            platform.yaml
            template1
            template2
            /forces
                variant1.yaml
                variant2.yaml
                /stage
                    file1
                    file2

Once a test output directory has been created, the templater will run each
batch script prefixed with "prepare" in the output directory. This is helpful
for setting permissions on shell scripts or copying files to variant directories.
These scripts should be placed in any ``stage`` directory to be copied over.

Adjusting Tests
---------------

Calling scripts and batch submission scripts are templated by parameters in test-specific
``.yaml`` files and platform-specific ``platform.yaml`` files. Each file contains
``"calling"`` and ``"submit"`` labels, corresponding to Jinja fields in the calling script
and batch submission script templates respectively.

Note the following about ``platform.yaml``:

    1) Parameters specified in ``platform.yaml`` don't have to be universal for all test types. For instance, ``"nthreads": 1`` can be included and templated for each WarpX test, but doesn't have to appear in Forces templates.
    2) Parameters in ``platform.yaml`` can also appear in test-specific configurations. Test configurations will override values from ``platform.yaml``.

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
