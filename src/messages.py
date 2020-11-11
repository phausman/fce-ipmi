POWER_LONG_HELP = """Control the power of one or more machines. You
can request powering on, off or power cycling the machine(s). `stat`
command reads the current power state of the machine(s).

If `power` command is run without a specified power action, the `stat`
action is executed by default.

This command is a wrapper for `ipmitool` utility. It executes `ipmitool`
with relevant parameters, such as `chassis power on`, `chassis power off`,
`chassis power status` or `chassis power cycle`.

EXAMPLES

Check power status of all machines:

    fce-ipmi power

Power on all machines:

    fce-ipmi power on

Power cycle all machines except storage nodes:

    fce-ipmi power cycle --exclude storage-*

Power cycle all machines except storage nodes tagged with `ssd`:

    fce-ipmi power cycle --exclude storage-*,tags=ssd

Power off only compute nodes:

    fce-ipmi power off compute-*

Power off only compute nodes in availability zone `AZ1`:

    fce-ipmi power off --include compute-*,zone=AZ1
"""

INCLUDE_OPTION_HELP = (
    "Pattern to match machines to be included in this command"
)

EXCLUDE_OPTION_HELP = (
    "Pattern to match machines to be excluded from this command"
)

POWER_COMMANDS_OPTIONS = """COMMAND OPTIONS

-i, --include PATTERN [NOT IMPLEMENTED]

The machines specified in the PATTERN will be included in the list of
machines selected for executing the command upon them.

Providing the MACHINE-NAME implicitly is an equivalent to specifying
`--include name=MACHINE-NAME`.

Multiple properties, separated by comma can be specified, e.g.
`--include name=storage-*,tags=AZ1`. The properties separated by comma are
applied according to logical 'AND' operation.

You can also specify multiple `--include` options. In such a case the
resulting list of machines will be the outcome of a logical 'OR' operation
between all `--include` options.

-x, --exclude PATTERN [NOT IMPLEMENTED]

This option excludes machines specified in the PATTERN from running the
action upon them.

By default, PATTERN applies to the machine name and is equivalent to
specifying `--exclude name=MACHINE-NAME`. You can specify other machine
properties, e.g. tags, zone, etc.

Similarly to `--include` option, this option also supports multiple
instances (joined as logical 'OR') and comma-separated properties."""

POWER_ON_ACTION_LONG_HELP = (
    """Power on one or more machines.

If MACHINE-NAME is not specified, the action is executed against all
machines.

Multiple MACHINE-NAMEs can be specified.

MACHINE-NAME accepts glob patterns. For example, running the command
`power on compute-*`, will result in powering on all machines whose name
begins with `compute-`.

You can specify a partial machine name and the program will try to guess
its full name. For example, if the machine's full name is
`compute-1.dc.example.com` it is enough to refer to this machine as
`compute-1`.

"""
    + POWER_COMMANDS_OPTIONS
)

POWER_OFF_ACTION_LONG_HELP = (
    """Power off one or more machines.

If MACHINE-NAME is not specified, the action is executed against all
machines.

Multiple MACHINE-NAMEs can be specified.

MACHINE-NAME accepts glob patterns. For example, running the command
`power off compute-*`, will result in powering off all machines whose name
begins with `compute-`.

You can specify a partial machine name and the program will try to guess
its full name. For example, if the machine's full name is
`compute-1.dc.example.com` it is enough to refer to this machine as
`compute-1`.

"""
    + POWER_COMMANDS_OPTIONS
)

POWER_CYCLE_ACTION_LONG_HELP = (
    """Power cycle one or more machines.

If MACHINE-NAME is not specified, the action is executed against all
machines.

Multiple MACHINE-NAMEs can be specified.

MACHINE-NAME accepts glob patterns. For example, running the command
`power cycle compute-*`, will result in powering cycling all machines whose
name begins with `compute-`.

You can specify a partial machine name and the program will try to guess
its full name. For example, if the machine's full name is
`compute-1.dc.example.com` it is enough to refer to this machine as
`compute-1`.

"""
    + POWER_COMMANDS_OPTIONS
)

POWER_STAT_ACTION_LONG_HELP = (
    """Read current power state of one or more machines.

If MACHINE-NAME is not specified, the action is executed against all
machines.

Multiple MACHINE-NAMEs can be specified.

MACHINE-NAME accepts glob patterns. For example, running the command
`power stat compute-*`, will result in reading power state of all machines
whose name begins with `compute-`.

You can specify a partial machine name and the program will try to guess
its full name. For example, if the machine's full name is
`compute-1.dc.example.com` it is enough to refer to this machine as
`compute-1`.

"""
    + POWER_COMMANDS_OPTIONS
)

#
# bootdev
#

BOOTDEV_LONG_HELP = """Set boot option for the next power cycle.

This command is a wrapper for `ipmitool` utility. It executes `ipmitool` with
relevant parameters, such as `chassis bootdev bios`, `chassis bootdev disk` or
`chassis bootdev pxe`.

EXAMPLES

Set boot to BIOS for all storage nodes:

    fce-ipmi bootdev bios storage-*

Set PXE boot for all nodes:

    fce-ipmi bootdev pxe

Set boot to disk for all machines in availability zones `AZ1` and `AZ2`

    fce-ipmi bootdev --include zone=AZ1 --include zone=AZ2
"""

BOOTDEV_COMMANDS_OPTIONS = POWER_COMMANDS_OPTIONS

BOOTDEV_DISK_ACTION_LONG_HELP = (
    """Force boot from default hard drive.

If MACHINE-NAME is not specified, the action is executed against all
machines.

Multiple MACHINE-NAMEs can be specified.

MACHINE-NAME accepts glob patterns. For example, running the command
`power on compute-*`, will result in powering on all machines whose name
begins with `compute-`.

You can specify a partial machine name and the program will try to guess
its full name. For example, if the machine's full name is
`compute-1.dc.example.com` it is enough to refer to this machine as
`compute-1`.

"""
    + POWER_COMMANDS_OPTIONS
)

BOOTDEV_BIOS_ACTION_LONG_HELP = (
    """Force boot into BIOS setup.

If MACHINE-NAME is not specified, the action is executed against all
machines.

Multiple MACHINE-NAMEs can be specified.

MACHINE-NAME accepts glob patterns. For example, running the command
`power on compute-*`, will result in powering on all machines whose name
begins with `compute-`.

You can specify a partial machine name and the program will try to guess
its full name. For example, if the machine's full name is
`compute-1.dc.example.com` it is enough to refer to this machine as
`compute-1`.

"""
    + POWER_COMMANDS_OPTIONS
)

BOOTDEV_PXE_ACTION_LONG_HELP = (
    """Force PXE boot.

If MACHINE-NAME is not specified, the action is executed against all
machines.

Multiple MACHINE-NAMEs can be specified.

MACHINE-NAME accepts glob patterns. For example, running the command
`power on compute-*`, will result in powering on all machines whose name
begins with `compute-`.

You can specify a partial machine name and the program will try to guess
its full name. For example, if the machine's full name is
`compute-1.dc.example.com` it is enough to refer to this machine as
`compute-1`.

"""
    + POWER_COMMANDS_OPTIONS
)

#
# console
#

CONSOLE_LONG_HELP = """Open a Serial-over-LAN console with a specified machine.

You can exit the console by typing '~.' sequence.

This command is a wrapper for `ipmitool sol activate`. The wrapper
executes `ipmitool` with relevant options such as a username and password.

EXAMPLE

Open the console with `compute-1` machine:

    fce-ipmi console compute-1
    """
