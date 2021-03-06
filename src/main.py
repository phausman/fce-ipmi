#!/usr/bin/env python3
"""Main module of the application.

Implements the entry point to the application and defines all
command line actions.
"""

from app import Application
from app import Command

import click

import messages

import version


VERSION = version.VERSION

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def print_version(ctx, param, value):
    """Print version of the application."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(VERSION)
    ctx.exit()


@click.group(help=messages.MAIN_HELP, context_settings=CONTEXT_SETTINGS)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    default=False,
    help="Enable debug log level.",
)
@click.option(
    "--dry-run",
    "-s",
    is_flag=True,
    default=False,
    help="Simulate running the command.",
)
@click.option(
    "-f",
    "--machine-config",
    default="./config/nodes.yaml",
    help="Path to the YAML file with machines' configuration.",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored output.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Be more verbose. [NOT IMPLEMENTED]",
)
@click.option(
    "--version",
    "-V",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Print program version.",
)
@click.pass_context
def cli(ctx, debug, dry_run, machine_config, no_color, verbose):
    """Define root of all commands."""
    # Ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if __name__ == "__main__"` block)
    ctx.ensure_object(dict)

    ctx.obj["debug"] = debug
    ctx.obj["dry_run"] = dry_run
    ctx.obj["no_color"] = no_color
    ctx.obj["verbose"] = verbose

    application = Application(
        debug=debug,
        machine_config=machine_config,
        dry_run=dry_run,
        no_color=no_color,
        verbose=verbose,
    )
    ctx.obj["app"] = application


#
# power (on|off|cycle|status)
#


@cli.group("power", help=messages.POWER_LONG_HELP, invoke_without_command=True)
@click.pass_context
def power(ctx):
    """Define the command group for `fce-ipmi power ...` commands."""
    # Call `power status` by default if no command action has been specified
    if ctx.invoked_subcommand is None:
        ctx.invoke(power_status)


@power.command("on", help=messages.POWER_ON_ACTION_LONG_HELP)
@click.argument("machine", nargs=-1, metavar="[MACHINE-NAME ...]")
@click.option(
    "-i",
    "--include",
    type=str,
    metavar="PATTERN",
    help=messages.INCLUDE_OPTION_HELP,
    multiple=True,
)
@click.option(
    "-x",
    "--exclude",
    type=str,
    metavar="PATTERN",
    help=messages.EXCLUDE_OPTION_HELP,
    multiple=True,
)
@click.pass_context
def power_on(ctx, machine, include, exclude):
    """Handle `fce-ipmi power on` command."""
    application = ctx.obj["app"]
    ctx.exit(application.run(Command.POWER_ON, machine, include, exclude))


@power.command("off", help=messages.POWER_OFF_ACTION_LONG_HELP)
@click.argument("machine", nargs=-1, metavar="[MACHINE-NAME ...]")
@click.option(
    "-i",
    "--include",
    type=str,
    metavar="PATTERN",
    help=messages.INCLUDE_OPTION_HELP,
    multiple=True,
)
@click.option(
    "-x",
    "--exclude",
    type=str,
    metavar="PATTERN",
    help=messages.EXCLUDE_OPTION_HELP,
    multiple=True,
)
@click.pass_context
def power_off(ctx, machine, include, exclude):
    """Handle `fce-ipmi powr off` command."""
    application = ctx.obj["app"]
    ctx.exit(application.run(Command.POWER_OFF, machine, include, exclude))


@power.command("cycle", help=messages.POWER_CYCLE_ACTION_LONG_HELP)
@click.argument("machine", nargs=-1, metavar="[MACHINE-NAME ...]")
@click.option(
    "-i",
    "--include",
    type=str,
    metavar="PATTERN",
    help=messages.INCLUDE_OPTION_HELP,
    multiple=True,
)
@click.option(
    "-x",
    "--exclude",
    type=str,
    metavar="PATTERN",
    help=messages.EXCLUDE_OPTION_HELP,
    multiple=True,
)
@click.pass_context
def power_cycle(ctx, machine, include, exclude):
    """Handle `fce-ipmi power cycle` command."""
    application = ctx.obj["app"]
    ctx.exit(application.run(Command.POWER_CYCLE, machine, include, exclude))


@power.command("status", help=messages.POWER_STATUS_ACTION_LONG_HELP)
@click.argument("machine", nargs=-1, metavar="[MACHINE-NAME ...]")
@click.option(
    "-i",
    "--include",
    type=str,
    metavar="PATTERN",
    help=messages.INCLUDE_OPTION_HELP,
    multiple=True,
)
@click.option(
    "-x",
    "--exclude",
    type=str,
    metavar="PATTERN",
    help=messages.EXCLUDE_OPTION_HELP,
    multiple=True,
)
@click.pass_context
def power_status(ctx, machine, include, exclude):
    """Handle `fce-ipmi power status` command."""
    application = ctx.obj["app"]
    ctx.exit(application.run(Command.POWER_STATUS, machine, include, exclude))


#
# bootdev (bios|disk|pxe)
#


@cli.group("bootdev", help=messages.BOOTDEV_LONG_HELP)
@click.pass_context
def bootdev(ctx):
    """Define the command group for `fce-ipmi bootdev ...` commands."""
    pass


@bootdev.command("disk", help=messages.BOOTDEV_DISK_ACTION_LONG_HELP)
@click.argument("machine", nargs=-1, metavar="[MACHINE-NAME ...]")
@click.option(
    "-i",
    "--include",
    type=str,
    metavar="PATTERN",
    help=messages.INCLUDE_OPTION_HELP,
    multiple=True,
)
@click.option(
    "-x",
    "--exclude",
    type=str,
    metavar="PATTERN",
    help=messages.EXCLUDE_OPTION_HELP,
    multiple=True,
)
@click.pass_context
def bootdev_disk(ctx, machine, include, exclude):
    """Handle `fce-ipmi bootdev disk` command."""
    application = ctx.obj["app"]
    ctx.exit(application.run(Command.BOOTDEV_DISK, machine, include, exclude))


@bootdev.command("bios", help=messages.BOOTDEV_BIOS_ACTION_LONG_HELP)
@click.argument("machine", nargs=-1, metavar="[MACHINE-NAME ...]")
@click.option(
    "-i",
    "--include",
    type=str,
    metavar="PATTERN",
    help=messages.INCLUDE_OPTION_HELP,
    multiple=True,
)
@click.option(
    "-x",
    "--exclude",
    type=str,
    metavar="PATTERN",
    help=messages.EXCLUDE_OPTION_HELP,
    multiple=True,
)
@click.pass_context
def bootdev_bios(ctx, machine, include, exclude):
    """Handle `fce-ipmi bootdev bios` command."""
    application = ctx.obj["app"]
    ctx.exit(application.run(Command.BOOTDEV_BIOS, machine, include, exclude))


@bootdev.command("pxe", help=messages.BOOTDEV_PXE_ACTION_LONG_HELP)
@click.argument("machine", nargs=-1, metavar="[MACHINE-NAME ...]")
@click.option(
    "-i",
    "--include",
    type=str,
    metavar="PATTERN",
    help=messages.INCLUDE_OPTION_HELP,
    multiple=True,
)
@click.option(
    "-x",
    "--exclude",
    type=str,
    metavar="PATTERN",
    help=messages.EXCLUDE_OPTION_HELP,
    multiple=True,
)
@click.pass_context
def bootdev_pxe(ctx, machine, include, exclude):
    """Handle `fce-ipmi bootdev pxe` command."""
    application = ctx.obj["app"]
    ctx.exit(application.run(Command.BOOTDEV_PXE, machine, include, exclude))


#
# console
#


@cli.command("console", help=messages.CONSOLE_LONG_HELP)
@click.argument("machine", metavar="MACHINE-NAME")
@click.pass_context
def console(ctx, machine):
    """Handle `fce-ipmi console` command."""
    # Application.run() operates on the list of machines
    machines = []
    machines.append(machine)

    application = ctx.obj["app"]
    ctx.exit(application.run(Command.CONSOLE, machines, None, None))


def init():
    """Execute cli() if module is run directly."""
    if __name__ == "__main__":
        cli(obj={})


init()
