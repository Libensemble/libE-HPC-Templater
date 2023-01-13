import os
import shutil
import subprocess
import sys
from pathlib import Path

import click

platform_base = Path(__file__).parent.absolute() / "platforms"
all_dir = platform_base / "all"
all_platforms = [x.stem for x in platform_base.iterdir() if x != all_dir]


def display_exit(ex):
    click.echo(str(ex))
    sys.exit(1)


def check_make_args(machine, tests, platform_dir):
    platform_test_strs = [i.stem for i in platform_dir.iterdir() if i.is_dir()]

    try:
        assert (
            machine in all_platforms
        ), "Specified machine is invalid. run `templater show machines` for valid targets."
        all_tests = [x.stem for x in all_dir.iterdir() if x.is_dir()]
        assert (
            tests == "all" or tests in all_tests
        ), "Specified test is invalid. use `all` or run `templater show tests` for valid targets."
    except AssertionError as ex:
        display_exit(ex)

    if tests != "all":
        try:
            assert tests in platform_test_strs, "Specified tests isn't supported."
        except AssertionError as ex:
            display_exit(ex)
        tests = [tests]
    else:
        tests = platform_test_strs

    return tests


def run_prepare_scripts(out_platform_dir):
    """Execute each additional shell script prepended with 'prepare'"""
    os.chdir(out_platform_dir)
    for file in os.listdir("."):
        if file.startswith("prepare"):
            subprocess.call(["./{}".format(file)])
    os.chdir("..")


def render(values, jinja_env):
    """Render a template with passed values"""
    chosen_template = values.get("template")
    template = jinja_env.get_template(chosen_template)

    return template.render(values)


def write_script(dir, name, values, jinja_env):
    """Write a rendered Jinja template"""
    with open(os.path.join(dir, name), "w") as f:
        f.write(render(values, jinja_env))


def make_out_platform_dir(platform, test, in_platform_dir):
    """Make a top-level directory labeled by platform and test name. Stage in files."""
    out_platform_dir = platform + "_" + test.split(".")[0]
    if not os.path.isdir(out_platform_dir):
        shutil.copytree(os.path.join(all_dir, test, "stage"), out_platform_dir)
        in_platform_stage = os.path.join(in_platform_dir, test, "stage")
        if not os.path.isdir(in_platform_stage):
            click.echo("\n Writing: ./" + str(out_platform_dir))
            return out_platform_dir
        for file in os.listdir(in_platform_stage):
            shutil.copy2(
                os.path.join(in_platform_stage, file),
                os.path.join(out_platform_dir, file),
            )

    click.echo("\n Writing: ./" + str(out_platform_dir))
    return out_platform_dir


def make_test_dir(out_platform_dir, variant):
    """Make a lower-level directory labeled by test name"""
    out_test_dir = os.path.join(out_platform_dir, "test_" + variant)
    os.makedirs(out_test_dir, exist_ok=True)

    click.echo("   --" + str(out_test_dir).split("/")[-1])
    return out_test_dir
