check_any_adjust = "- Optionally make test-specific adjustments to the .json files in ./platforms/PLATFORM/TEST"
check_balsam1 = "- If testing with Balsam1, install via pip: [pip install balsam-flow]\n" + \
               "- Then, initalize a database with: [balsam init ~/my_workflow]\n"

check_balsam2 = """
- If testing with Balsam2, install via pip: [pip install balsam]
- Then:

    balsam login
    balsam site init ./my-site
    cd my-site; balsam site start

Authenticate with ALCF credentials when asked.

If either of your Balsam ApplicationDefinitions (RemoteForces or RemoteLibensembleApp)
haven't been synced/updated recently, do so by editing and running define_apps.py

(I'll support templating define_apps.py in the future)

This includes, if not using transfers, commenting-out the transfers block for RemoteForces.

The easiest evaluation of the run's success at this point will be checking the
Balsam site's data directory.
"""

notice = "NOTICE:\nMany of the templater's produced tests may require " + \
      "additional\nPython, module, or application builds and adjustments before " + \
      "they will\nfunction. The following adjustments " + \
      "can be made on a test-by-test basis\nafter templating, but we " + \
      "recommend performing them prior:\n"

see_docs = "Platform documentation and guides: https://libensemble.readthedocs.io/en/develop/platforms/platforms_index.html#instructions-for-specific-platforms\n"
