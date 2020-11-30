# THIS LOOKS UGLY AND SET UP IN AN UNNECESSARY WAY. In theory, it should be easier
#  this way to add additional system-test-specific descriptive lines for each pair.

check_warpx_built = "- Make sure WarpX is built, and the paths match in ./platforms/PLATFORM/platform.json\n"
check_conda_env = "- Make sure your Conda environment matches in ./platforms/PLATFORM/platform.json\n"
check_any_adjust = "- Optionally make test-specific adjustments to the .json files in ./platforms/PLATFORM/TEST\n"
check_balsam = "- If testing with Balsam, install via pip [pip install balsam-flow]\n" + \
               "- Then, initalize a database with [balsam init ~/my_workflow]\n" + \
               "- Make sure this database matches in ./platforms/PLATFORM/platform.json\n"

base_warpx = check_warpx_built + check_conda_env + check_any_adjust
base_forces = check_conda_env + check_any_adjust
# Add instructions for each by appending additional strings

instructions = {
    ('summit', 'warpx'): base_warpx,
    ('summit', 'forces'): base_forces,
    ('bebop', 'warpx'): check_warpx_built + check_any_adjust,
    ('bebop', 'forces'): check_any_adjust,
    ('cori', 'warpx'): base_warpx,
    ('cori', 'forces'): base_forces,
    ('theta', 'warpx'): base_warpx + check_balsam,
    ('theta', 'forces'): base_forces + check_balsam,
    ('bridges', 'warpx'): base_warpx,
    ('bridges', 'forces'): base_forces
}

notice = "NOTICE:\nMany of the templater's produced tests may require " + \
      "additional\nPython, module, or application builds and adjustments before " + \
      "they will\nfunction. The following adjustments " + \
      "can be made on a test-by-test basis\nafter templating, but we " + \
      "recommend performing them prior:\n"

see_docs = "Platform documentation and guides: https://libensemble.readthedocs.io/en/develop/platforms/platforms_index.html#instructions-for-specific-platforms\n"
