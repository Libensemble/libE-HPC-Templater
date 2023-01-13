#!/usr/bin/env python

import os
import sys
import json
import click
import shutil
import pprint
import argparse
import subprocess
import click
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

platform_base = Path(__file__).parent.absolute() / "platforms"
all_dir = platform_base / "all"
all_platforms = [x.stem for x in platform_base.iterdir() if x != all_dir]
all_tests = [x.stem for x in all_dir.iterdir() if x.is_dir()]

def display_exit(ex):
    click.echo(str(ex))
    sys.exit(1)

def make_out_platform_dir(platform, test, in_platform_dir):
    """ Make a top-level directory labeled by platform and test name. Stage in files."""
    out_platform_dir = platform + '_' + test.split('.')[0]
    if not os.path.isdir(out_platform_dir):
        shutil.copytree(os.path.join(all_dir, test, "stage"), out_platform_dir)
        in_platform_stage = os.path.join(in_platform_dir, test, "stage")
        if not os.path.isdir(in_platform_stage):
            print("\n Writing: ./" + out_platform_dir)
            return out_platform_dir
        for file in os.listdir(in_platform_stage):
            shutil.copy2(os.path.join(in_platform_stage, file),
                         os.path.join(out_platform_dir, file))

    print("\n Writing: ./" + out_platform_dir)
    return out_platform_dir

@click.command()
@click.argument("path", nargs=1)
def check(path):
    """Check a tests directory (or `all`) for passes/fails."""
    click.echo("checking")


@click.command()
@click.argument("path", nargs=1)
def submit(path):
    """Try submitting each of the tests in a directory (or `all`)."""
    click.echo("submitting")


@click.command()
@click.argument("machine", nargs=1)
@click.argument("test", nargs=1)
def make(machine, test):
    """Make tests by machine and variant (or `all`)."""
    try:
        assert machine in all_platforms, "Specified machine is invalid. run `templater show machines` for valid targets."
        assert test == "all" or test in all_tests, "Specified test is invalid. use `all` or run `templater show tests` for valid targets."
    except AssertionError as ex:
        display_exit(ex)

    platform_dir = platform_base / machine
    platform_test_dirs = [i for i in platform_dir.iterdir() if i.is_dir()]
    platform_test_strs = [i.stem for i in platform_test_dirs]
    if test != "all":
        try:
            assert test in platform_test_strs, "Specified test isn't supported."
        except AssertionError as ex:
            display_exit(ex)
    else:
        test = platform_test_strs

    file_loader = FileSystemLoader(platform_dir)
    jinja_env = Environment(loader=file_loader, lstrip_blocks=True)

    with open(platform_dir / "platform.json") as p:
        platform_values = json.load(p)

    for t in test:
        in_test_dir = platform_dir / t
        variant_files = [i for i in in_test_dir.glob("*.json")]
        import ipdb; ipdb.set_trace()
        pass

    pass


@click.command()
@click.argument("platform", nargs=1)
def config(platform):
    """Edit the base settings for a given machine."""
    platform_file = platform_base / platform / "platform.json"
    config_label = (
        "\n" + platform.title() + " Configuration: " + str(platform_file) + "\n"
    )
    click.echo(config_label)
    click.echo("-" * (len(config_label) - 3) + "\n")
    with open(platform_file, "r") as f:
        platform_values = json.load(f)

    pprint.pprint(platform_values)
    adjust = input("\nAdjust any of the above platform parameters? (Y/N): ")
    if adjust.upper() == "Y":
        subprocess.call([os.environ.get("EDITOR", "vim"), platform_file])
        print(str(platform_file), "adjusted.")


# ---

@click.command()
def ls():
    """Display all currently supported machines and their tests"""
    click.echo("Supported Machines and Tests:")
    for x in all_platforms:
        out = "   - {}: "
        out = out.format(x.title()).ljust(14)
        platform_dir = platform_base / x
        platform_tests = [i for i in platform_dir.iterdir() if i.is_dir()]
        for i in platform_tests:
            out += str(i.stem) + ", "
        click.echo(out)


@click.group()
def _main():
    """libEnsemble Scaling Tests Templater

    Make test-specific adjustments to the .json files in libE-templater/platforms/PLATFORM/TEST
    """
    pass


_main.add_command(check)
_main.add_command(submit)
_main.add_command(make)
_main.add_command(config)
_main.add_command(ls)

if __name__ == "__main__":
    _main()
