import os

import click
from dotenv import load_dotenv

from . import __version__
from .cmd.bootstrap import bootstrap
from .cmd.graph import graph
from .cmd.ls import ls
from .cmd.sync import sync
from .context import Context
from .log import FatalError

load_dotenv()


@click.group()
@click.version_option(__version__)
@click.option('--workspace', default='.', required=True, show_default=True, show_envvar=True,
              type=click.Path(exists=True, file_okay=False, writable=True),
              help='Path to the workspace directory.')
@click.option('-p', '--profile', default='all', required=True, show_default=True, show_envvar=True,
              metavar='NAME', help='Name of the workspace profile to operate in.')
# Default value same as for ThreadPoolExecutor on Python 3.8
@click.option('-j', '--jobs', type=click.IntRange(min=1), default=max(32, os.cpu_count() + 4),
              required=True, show_default=True, show_envvar=True, metavar='COUNT',
              help='Set number of parallel running jobs.')
@click.option('--github_access_token', required=True, show_envvar=True, metavar='TOKEN',
              help='Github private access token.')
def cli(**kwargs):
    Context.initial(**kwargs)


cli.add_command(bootstrap)
cli.add_command(graph)
cli.add_command(ls)
cli.add_command(sync)

try:
    cli(auto_envvar_prefix='SEBEX')
except FatalError:
    pass
