import click
from click_aliases import ClickAliasedGroup

@click.command()
@click.argument('path', nargs=1)
def check(args):
    pass

@click.command()
@click.argument('args', nargs=2)
def run(args):
    pass

@click.command()
@click.argument('args', nargs=2)
def make(args):
    pass

@click.command()
@click.argument('arg', nargs=1)
def config(args):
    pass



# ---

@click.group(cls=ClickAliasedGroup)
@click.argument('arg', nargs=1)
def show(arg):
    pass

@show.command(aliases=['m', 'platforms', 'p'])
def machines():
    pass

@show.command(aliases=['t'])
def tests():
    pass

@click.group()
def _main():
    pass

_main.add_command(check)
_main.add_command(run)
_main.add_command(make)
_main.add_command(config)
_main.add_command(show)

if __name__ == "__main__":
    _main()