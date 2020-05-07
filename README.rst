libE-templater
==============

Generate libEnsemble testing scripts from templates for a variety of HPC platforms.

Requires Jinja:

https://jinja.palletsprojects.com/en/2.11.x/

``pip install Jinja2``

Supported platforms are LCRC's Bebop, ALCF's Theta, NERSC's Cori, and
OLCF's Summit. Specify any specific platform to generate a testing environment
at runtime with any number of ``--bebop``, ``--theta``, ``--cori``, and ``--summit``.

Currently generates testing environments for the Forces and WarpX scaling tests.
Use ``--forces`` and ``--warpx``.

Usage
-----

- Make all tests for a single platform:

    ``./templater.py --theta --all``

- Make only forces tests:

    ``python templater.py --cori --forces``

Configuration
-------------

A list of all tests are found in ``config.json`` in the project root,
organized by platform, then test type, then test variant. When adding a new test
variant, make sure the variant name matches the filenames of the associated
configuration files. For example, Bebop's Forces calling and submission
template configurations named ``MPI_central.json`` match ``MPI_central`` in
``config.json``.

The ``platforms`` directory contains both platform-specific test configurations
and templates in ``bebop``, ``cori``, ``summit``, and ``theta``, and platform-agnostic
configurations and templates in ``all``. Each of these directories contains
templates and directories for each supported test. For instance, ``platforms/summit``
contains the ``forces`` and ``warpx`` test directories then a template.

A test directory like ``forces`` contains two or three subdirectories:
``calling``, ``submit``, and optionally ``stage``. ``calling`` and ``submit`` contain
configurations for the test variant's calling and batch submission scripts,
respectively. ``submit`` also contains the ``platform.json`` configuration file
for submission scripts to specify submission script attributes that are universal
on a platform. ``stage`` can contain test-specific files to copy to each test's
output directory.

Once a test output directory has been created, the templater will run each
batch script prefixed with "prepare" in the output directory. This is helpful
for setting permissions on copied shell scripts or copying additional files around
if necessary. These scripts should be placed in any ``stage`` directory to be
copied over.

Example
-------

Suppose we want to define a new test ``"particles"``, only for Theta, with ``mpi_128-nodes``
and ``multiprocess_64-nodes`` variants.

1) Add the following configuration to ``config.json`` under ``"Theta"``::


    "particles":[
        "mpi_128-nodes",
        "multiprocess_64-nodes"
    ]

2) Add "particles" to ``tests`` in the templater script.

3) Place calling script and batch-submission script Jinja templates in ``platforms/theta``.
Create a test directory, ``platforms/theta/particles``.

4) Create ``calling``, ``submit`` directories in this test directory. If there are
files that should be copied over (not templated) to the output directory, create
``stage`` and place those files there.

5) Make configuration files for the calling script, named ``mpi_128-nodes.json``
and ``multiprocess_64-nodes.json`` and place within ``calling``. Fields can
template any parameter you wish for the calling scripts, but must also contain
a ``"template"`` field referencing which template the configuration should populate.
Do the same for the submission script in ``submit``.

6) For the submission script, any platform-specific parameters that shouldn't be
different between tests should be placed in a ``platform.json``.
