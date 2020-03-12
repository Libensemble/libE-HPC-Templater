import os
import sys
import json
import shutil
import argparse
from jinja2 import Environment, FileSystemLoader


platforms = ["bebop", "summit", "theta", "cori"]
types = ["calling", "submit"]


def parse_options():
    """ Return user command-line platform and script type args as dictionary"""
    parser = argparse.ArgumentParser(description="Pass machine names and " + \
                                                 "script types for templating")

    for i in platforms + types + ["all", "both"]:
        parser.add_argument('--' + i, action='store_true')

    options = vars(parser.parse_args(sys.argv[1:]))
    assert any([options[i] for i in platforms + ["all"]]), \
        "No targets. Specify platform(s) (e.g., --theta --summit) or --all"

    return options


def determine_source_dirs(options):
    """ Determine directories that contain configurations for test templates"""
    if options["all"]:
        req_platforms = platforms
    else:
        req_platforms = [i for i in platforms if options[i]]

    if options["both"] or (not options["calling"] and not options["submit"]):
        req_types = types
    else:
        req_types = [i for i in types if options[i]]

    source_dirs = []
    for p in req_platforms:
        for t in req_types:
            source_dirs.append(os.path.join(p, t + '_values'))

    return source_dirs


def prepare_jinja(templates):
    """ Setup jinja environment and get current platform templates folder"""
    file_loader = FileSystemLoader(templates)
    jinja_env = Environment(loader=file_loader, lstrip_blocks=True)

    return jinja_env


def get_tests_properties(dir):
    """ Determine a number of test properties from a source directory"""
    platform = dir.split('/')[0]
    type = dir.split('_')[0].split('/')[1]
    templates = os.path.join(platform, "templates")
    config_source = os.path.join(platform, "test_config")

    with open(os.path.join(config_source, "tests.json")) as t:
        tests = json.load(t)

    return tests, platform, type, templates, config_source


def make_platform_dir(platform, test, config_source):
    """ Make a top-level directory labeled by platform and test name"""
    platform_dir = platform + '_' + test.split('.')[0]
    if not os.path.isdir(platform_dir):
        shutil.copytree(config_source, platform_dir,
                        ignore=shutil.ignore_patterns('tests.json'))

    return platform_dir


def make_test_dir(config, platform_dir):
    """ Make a lower-level directory labeled by test name"""
    test_dir = config.split('.')[0]
    full_dir = os.path.join(platform_dir, test_dir)
    os.makedirs(full_dir, exist_ok=True)

    return test_dir, full_dir


def render(values, jinja_env):
    """ Render a template with passed values"""
    chosen_template = values.get("template")
    template = jinja_env.get_template(chosen_template)

    return template.render(values)


def render_calling(dir, config, test, jinja_env, full_dir):
    """ Load configs for a calling script, output rendered template"""
    with open(os.path.join(dir, config), "r") as r:
        run_values = json.load(r)

    with open(os.path.join(full_dir, test), "w") as f:
        f.write(render(run_values, jinja_env))


def render_submit(dir, config, test, jinja_env, full_dir, test_dir):
    """ Load configs for a job submission script, output rendered template"""
    with open(os.path.join(dir, config), "r") as r:
        run_values = json.load(r)

    with open(os.path.join(dir, "platform.json")) as p:
        platform_values = json.load(p)

    single_test = {"test": test}
    combined = {**run_values, **single_test, **platform_values}

    with open(os.path.join(full_dir, 'submit_' + test_dir + '.sh'), "w") as f:
        f.write(render(combined, jinja_env))


is_test = lambda x: x != "platform.json"


if __name__ == '__main__':

    for dir in determine_source_dirs(parse_options()):
        tests, platform, type, templates, config_source = get_tests_properties(dir)
        jinja_env = prepare_jinja(templates)

        for test in tests.get("tests"):
            platform_dir = make_platform_dir(platform, test, config_source)

            for config in os.listdir(dir):
                if is_test(config):
                    test_dir, full_dir = make_test_dir(config, platform_dir)

                if type == "calling":
                    render_calling(dir, config, test, jinja_env, full_dir)

                elif type == "submit":
                    if is_test(config):
                        render_submit(dir, config, test, jinja_env, full_dir, test_dir)
