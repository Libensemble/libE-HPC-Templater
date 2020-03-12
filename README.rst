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

- Add any combination of ``--bebop``, ``--summit``, etc., to make tests for those
  platforms.

- Make only calling scripts or submission scripts:

    ``python template_hpc.py --all --calling`` OR ``python template_hpc.py --all --submit``

Configuration
-------------

- Each platform has its own input directory structure:

```
    - [platform]
        - calling_values
        - submit_values
        - templates
        - test_config
```

- calling_values: Per-test configurations for test calling scripts.

- submit_values: Per-test configurations for test job submission scripts, and
                 ``platform.json``, with platform-specific universal
                 submission script settings.

- templates: Templates for submission scripts and calling scripts.

- test_config: ``tests.json``, a list of tests to create scripts for, and other
               files to copy to each upper-level platform directory.
