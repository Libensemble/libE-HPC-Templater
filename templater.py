#!/usr/bin/env python

import os
import sys
import json
import shutil
import argparse
import subprocess
from jinja2 import Environment, FileSystemLoader


platform_base = "./platforms"
all_dir = os.path.join(platform_base, "all")

platforms = ["bebop", "summit", "theta", "cori"]
# types = ["calling", "submit"]
tests = ["forces", "warpx"]
test_templates = {'forces': 'run_libe_forces.py', 'warpx': 'run_libensemble_on_warpx.py'}


def parse_options():
    """ Return user command-line platform and script type args as dictionary"""
    parser = argparse.ArgumentParser(description="Pass machine names and " + \
                                                 "test names for templating")

    for i in platforms + tests + ["all"]:
        parser.add_argument('--' + i, action='store_true')

    options = vars(parser.parse_args(sys.argv[1:]))
    assert any([options[i] for i in platforms + ["all"]]), \
        "No targets. Specify platform(s) (e.g., --theta --summit) or --all"

    return options


def determine_requests(options):
    """ Determine directories that contain configurations for test templates"""
    if options["all"]:
        req_platforms = platforms
        req_tests = tests
    else:
        req_platforms = [i for i in platforms if options[i]]
        req_tests = [i for i in tests if options[i]]

    return req_platforms, req_tests


def prepare_jinja(templates):
    """ Setup jinja environment and get current templates folder"""
    file_loader = FileSystemLoader(templates)
    jinja_env = Environment(loader=file_loader, lstrip_blocks=True)

    return jinja_env


def get_tests(platform):
    """ Determine set of tests to populate templates for"""
    with open("config.json") as f:
        tests = json.load(f)

    return [i for i in tests[platform]]


def make_out_platform_dir(platform, test, in_platform_dir):
    """ Make a top-level directory labeled by platform and test name. Stage in files."""
    out_platform_dir = platform + '_' + test.split('.')[0]
    if not os.path.isdir(out_platform_dir):
        shutil.copytree(os.path.join(all_dir, test, "stage"), out_platform_dir)
        in_platform_stage = os.path.join(in_platform_dir, test, "stage")
        for file in os.listdir(in_platform_stage):
            shutil.copy2(os.path.join(in_platform_stage, file),
                         os.path.join(out_platform_dir, file))

    return out_platform_dir


def make_test_dir(out_platform_dir, config):
    """ Make a lower-level directory labeled by test name"""
    out_test_dir = os.path.join(out_platform_dir, "test_" + config.split('.')[0])
    os.makedirs(out_test_dir, exist_ok=True)

    return out_test_dir


def load_config(in_type_dir, config):
    """ Load current configuration file"""
    with open(os.path.join(in_type_dir, config), "r") as r:
        values = json.load(r)

    return values

def render(values, jinja_env):
    """ Render a template with passed values"""
    chosen_template = values.get("template")
    template = jinja_env.get_template(chosen_template)

    return template.render(values)


def render_calling(values, out_test_dir, test, jinja_env):
    """ Load configs for a calling script, output rendered template"""
    with open(os.path.join(out_test_dir, test), "w") as f:
        f.write(render(values, jinja_env))


def render_submit(values, out_test_dir, test, jinja_env):
    """ Load configs for a job submission script, output rendered template"""
    with open(os.path.join(in_type_dir, "platform.json")) as p:
        platform_values = json.load(p)

    single_test = {"test": test}
    combined = {**single_test, **platform_values, **values}

    with open(os.path.join(out_test_dir, 'submit_' + config.split('.')[0] + '.sh'), "w") as f:
        f.write(render(combined, jinja_env))


def run_prepare_scripts(out_platform_dir):
    os.chdir(out_platform_dir)
    for file in os.listdir('.'):
        if file.startswith('prepare'):
            subprocess.call(['./{}'.format(file)])
    os.chdir('..')


is_test = lambda x: x != "platform.json"


if __name__ == '__main__':
    platforms, tests = determine_requests(parse_options())

    for platform in platforms:
        in_platform_dir = os.path.join(platform_base, platform)
        jinja_env = prepare_jinja([in_platform_dir, all_dir])

        for test in get_tests(platform):
            import ipdb; ipdb.set_trace()
            out_platform_dir = make_out_platform_dir(platform, test, in_platform_dir)

            for type in types:
                in_type_dir = os.path.join(in_platform_dir, type)

                for config in os.listdir(in_type_dir):
                    if is_test(config):
                        out_test_dir = make_test_dir(out_platform_dir, config)

                    values = load_config(in_type_dir, config)

                    if type == "calling":
                        render_calling(values, out_test_dir, test, jinja_env)

                    elif type == "submit":
                        if is_test(config):
                            render_submit(values, out_test_dir, test, jinja_env)

            run_prepare_scripts(out_platform_dir)
