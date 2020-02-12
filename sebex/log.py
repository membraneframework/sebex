import click


def log(*msg, color=None):
    message = ' '.join(str(m) for m in msg)
    if color is not None:
        message = click.style(message, fg=color)
    click.echo(message)


def success(*msg):
    log(*msg, color='green')


def warn(*msg):
    log(*msg, color='yellow')


def error(*msg):
    log(*msg, color='red')


class FatalError(Exception):
    pass


def fatal(*msg):
    error('FATAL:', *msg)
    raise FatalError()