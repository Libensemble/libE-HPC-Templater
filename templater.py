import os
import sys
import json
import shutil
import argparse
from jinja2 import Environment, FileSystemLoader

platform_src = "./platforms"

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


def determine_requests(options):
    """ Determine directories that contain configurations for test templates"""
    if options["all"]:
        req_platforms = platforms
    else:
        req_platforms = [i for i in platforms if options[i]]

    if options["both"] or (not options["calling"] and not options["submit"]):
        req_types = types
    else:
        req_types = [i for i in types if options[i]]

    return req_platforms, req_types


def prepare_jinja(templates):
    """ Setup jinja environment and get current templates folder"""
    file_loader = FileSystemLoader(templates)
    jinja_env = Environment(loader=file_loader, lstrip_blocks=True)

    return jinja_env


def get_tests(platform_dir):
    """ Determine set of tests to populate templates for"""
    with open(os.path.join(platform_dir, "tests.json")) as f:
        tests = json.load(f)

    return tests.get("tests")


def make_out_platform_dir(platform, test):
    """ Make a top-level directory labeled by platform and test name"""
    out_platform_dir = platform + '_' + test.split('.')[0]
    os.makedirs(out_platform_dir, exist_ok=True)

    return out_platform_dir
    # if not os.path.isdir(platform_dir):
    #     shutil.copytree(config_source, platform_dir,
    #                     ignore=shutil.ignore_patterns('tests.json'))


def make_test_dir(out_platform_dir, config):
    """ Make a lower-level directory labeled by test name"""
    out_test_dir = os.path.join(out_platform_dir, config.split('.')[0])
    os.makedirs(out_test_dir, exist_ok=True)

    return out_test_dir


def render(values, jinja_env):
    """ Render a template with passed values"""
    chosen_template = values.get("template")
    template = jinja_env.get_template(chosen_template)

    return template.render(values)


def render_calling(in_type_dir, config, out_test_dir, test, jinja_env):
    """ Load configs for a calling script, output rendered template"""
    with open(os.path.join(in_type_dir, config), "r") as r:
        values = json.load(r)

    with open(os.path.join(out_test_dir, test), "w") as f:
        f.write(render(values, jinja_env))


def render_submit(in_type_dir, config, out_test_dir, test, jinja_env):
    """ Load configs for a job submission script, output rendered template"""
    with open(os.path.join(in_type_dir, config), "r") as r:
        values = json.load(r)

    with open(os.path.join(in_type_dir, "platform.json")) as p:
        platform_values = json.load(p)

    single_test = {"test": test}
    combined = {**values, **single_test, **platform_values}

    with open(os.path.join(out_test_dir, 'submit_' + config.split('.')[0] + '.sh'), "w") as f:
        f.write(render(combined, jinja_env))


is_test = lambda x: x != "platform.json"


if __name__ == '__main__':
    platforms, types = determine_requests(parse_options())

    for platform in platforms:
        in_platform_dir = os.path.join(platform_src, platform)
        jinja_env = prepare_jinja([in_platform_dir, os.path.join(platform_src, "all")])

        for test in get_tests(in_platform_dir):
            out_platform_dir = make_out_platform_dir(platform, test)

            for type in types:
                in_type_dir = os.path.join(in_platform_dir, type)

                for config in os.listdir(in_type_dir):
                    if is_test(config):
                        out_test_dir = make_test_dir(out_platform_dir, config)

                    if type == "calling":
                        render_calling(in_type_dir, config, out_test_dir, test, jinja_env)

                    elif type == "submit":
                        if is_test(config):
                            render_submit(in_type_dir, config, out_test_dir, test, jinja_env)
