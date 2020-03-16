libE-templater
==============

Generate libEnsemble testing scripts from templates for a variety of HPC platforms.

Requires Jinja:

https://jinja.palletsprojects.com/en/2.11.x/

``pip install Jinja2``

Currently supported platforms are LCRC's Bebop, ALCF's Theta, NERSC's Cori, and
OLCF's Summit.

Usage
-----

- Make all tests for all platforms (bebop, theta, cori, summit):

    ``python template_hpc.py --all``

- Make all tests for a single platform:

    ``python template_hpc.py --theta``

- Add any combination of ``--bebop``, ``--summit``, etc., to make tests for those platforms.

- Make only calling scripts or submission scripts:

    ``python template_hpc.py --all --calling`` OR ``python template_hpc.py --all --submit``

The files within ``platforms/all/stage`` and ``platforms/[platform]/stage`` are
copied into each platform-specific output directory.


Configuration
-------------

- Each platform has its own input directory structure::

    - [platform]/
        - calling/
        - submit/
        - stage/
        - tests.json
        - [templates]

- calling: Per-test configurations for test calling scripts.

- submit: Per-test configurations for test job submission scripts, and ``platform.json``, with platform-specific universal submission script settings.

- stage: Files to copy over to each test directory

- tests.json: A set of tests to configure scripts for on this platform.

and then any number of templates specific to this platform.
