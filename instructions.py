# THIS LOOKS UGLY AND SET UP IN AN UNNECESSARY WAY. In theory, it should be easier
#  this way to add additional system-test-specific descriptive lines for each pair.

check_warpx_built = "- Make sure WarpX is built, and the path in ./platforms/all/warpx/stage/all_machine_specs.py matches.\n"
check_conda_env = "- Make sure your Conda environment matches in ./platforms/PLATFORM/platform.json\n"
check_any_adjust = "- Optionally make test-specific adjustments to the .json files in ./platforms/PLATFORM/TEST\n"

# Add instructions for each by appending additional strings

instructions = {
    ('summit', 'warpx'): check_warpx_built + check_conda_env + check_any_adjust,
    ('summit', 'forces'): check_conda_env + check_any_adjust,
    ('bebop', 'warpx'): check_warpx_built + check_conda_env + check_any_adjust,
    ('bebop', 'forces'): check_conda_env + check_any_adjust,
    ('cori', 'warpx'): check_warpx_built + check_conda_env + check_any_adjust,
    ('cori', 'forces'): check_conda_env + check_any_adjust,
    ('theta', 'warpx'): check_warpx_built + check_conda_env + check_any_adjust,
    ('theta', 'forces'): check_conda_env + check_any_adjust,
}

notice = "NOTICE:\nMany of the templater's produced tests may require " + \
      "additional\nPython, module, or application builds and adjustments before " + \
      "they will\nfunction. The following adjustments " + \
      "can be made on a test-by-test basis\nafter templating, but we " + \
      "recommend performing them ahead of time:\n"
