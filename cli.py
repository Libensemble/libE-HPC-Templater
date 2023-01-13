#!/usr/bin/env python

import json
import os
import pprint
import subprocess
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader

from utils import (
    check_make_args,
    display_exit,
    make_out_platform_dir,
    make_test_dir,
    run_prepare_scripts,
    write_script,
)

platform_base = Path(__file__).parent.absolute() / "platforms"
all_dir = platform_base / "all"
all_platforms = [x.stem for x in platform_base.iterdir() if x != all_dir]


@click.command()
@click.argument("path", nargs=1)
def check(path):
    """Check a test directory (or `all`) for passes/fails."""
    click.echo("checking")


@click.command()
@click.argument("path", nargs=1)
def submit(path):
    """Try submitting each of the tests in a directory (or `all`)."""
    click.echo("submitting")


@click.command()
@click.argument("machine", nargs=1)
@click.argument("tests", nargs=1)
def make(machine, tests):
    """Make tests by machine and variant (or `all`)."""

    platform_dir = platform_base / machine
    tests = check_make_args(machine, tests, platform_dir)

    file_loader = FileSystemLoader([platform_dir, all_dir])
    jinja_env = Environment(loader=file_loader, lstrip_blocks=True)

    with open(platform_dir / "platform.json") as p:
        platform_values = json.load(p)

    for test in tests:
        in_test_dir = platform_dir / test
        variant_files = [i for i in in_test_dir.glob("*.json")]
        out_platform_dir = make_out_platform_dir(machine, test, platform_dir)

        for variant in variant_files:
            with open(variant) as f:
                variant_config = json.load(f)

            calling_values = variant_config["calling"]
            submit_values = variant_config["submit"]
            single_test = {"tests": calling_values["template"]}
            submit_values = {
                **single_test,
                **platform_values["submit"],
                **submit_values,
            }
            calling_values = {**platform_values["calling"], **calling_values}

            variant_str = variant.stem.split(".json")[0]

            out_test_dir = make_test_dir(out_platform_dir, variant_str)
            write_script(
                out_test_dir, calling_values["template"], calling_values, jinja_env
            )
            write_script(
                out_test_dir,
                "submit_" + variant_str,
                submit_values,
                jinja_env,
            )

        run_prepare_scripts(out_platform_dir)


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
def main():
    """libEnsemble Scaling Tests Templater

    Make test-specific adjustments to the .json files in libE-templater/platforms/PLATFORM/TEST
    """
    pass


main.add_command(check)
main.add_command(submit)
main.add_command(make)
main.add_command(config)
main.add_command(ls)

if __name__ == "__main__":
    main()
