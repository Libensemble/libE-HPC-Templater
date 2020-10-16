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

Additional options are supported automatically if corresponding
platform and test directories are created. For instance, adding a platform ``foo``
with test directory ``foo/bar`` enables `` --foo --bar`` options.

Usage
-----

- Make all tests for a single platform:

    ``./templater --theta --all``

- Make only Forces tests for Cori:

    ``./templater --cori --forces``

Users are presented with reminders on how they may need to customize or prepare
their working environment or test configurations prior to templating. In the
event that previous templated tests are detected, the templater can assist the
user with either removing the previous templated test directory, or overwriting
specific test cases.

Configuration
-------------

The ``platforms`` directory contains platform-specific test configurations
and templates in ``bebop``, ``cori``, ``summit``, and ``theta``, and platform-agnostic
configurations and templates in ``all``. Each of these directories contains
sub-directories, templates, and configurations for each supported test. For example,
``platforms/bebop`` contains ``forces`` and ``warpx`` directories that match both supported tests,
two different templates for submission scripts (used by both tests), and ``platform.json``,
containing platform-specific submission script parameters.

As an example, ``platforms/bebop/forces`` contains both a ``stage`` directory
and multiple ``.json`` files. Each ``.json`` file corresponds to a variant of ``forces``,
with different numbers of nodes, comm-types, etc. that can be tested on ``bebop``.
``stage`` contains files to be copied to the output test-directory ``bebop_forces``.::

    /platforms
        /bebop
            platform.json
            template1
            template2
            /forces
                variant1.json
                variant2.json
                /stage
                    file1
                    file2

Once a test output directory has been created, the templater will run each
batch script prefixed with "prepare" in the output directory. This is helpful
for setting permissions on copied shell scripts or copying additional files around
if necessary. These scripts should be placed in any ``stage`` directory to be
copied over.

Example
-------

Suppose we want to define a new test ``"particles"``, only for Theta, with ``mpi_128-nodes``
and ``multiprocess_64-nodes`` variants.

1) Place Jinja templates for calling scripts and submission scripts in ``platforms/all``
or ``platforms/theta``.

2) Create a test directory, ``platforms/theta/particles``.

3) Place configuration ``.json`` files to populate templates within this new directory.
In this case, they'll be named ``mpi_128-nodes.json`` and ``multiprocess_64-nodes.json``.
They must contain ``"calling"`` and ``"submit"`` keys matching a ``"template"``
key-value pairs and any number of other key-value pairs.
For example::

    {
        "calling": {
            "sample_parameter": true,
            "template": "my_calling_template.py"
        },

        "submit": {
            "another_parameter": 123,
            "template": "my_submission_template.sh"
        }
    }

4) Append reminders and instructions for this test to ``instructions`` in ``strings.py``

5) (Optional) place files to copy over to the eventual output directory, ``theta_particles``,
within a new directory ``stage`` inside the above test directory.
