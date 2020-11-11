# Introduction

`fce-ipmi` is a tool that simplifies interaction with `ipmitool` utility while
working with multiple bare-metal machines.

Supported commands:
- `power {on|off|cycle|stat}` controls the power of the machine(s),
- `bootdev {bios|disk|pxe}` forces a boot option,
- `console` opens a SOL console with a machine.

Example: check power status of all machines:

    $ fce-ipmi power stat compute-*
    INFO: compute-1: Chassis Power is off
    INFO: compute-2: Chassis Power is on
    INFO: compute-3: Chassis Power is off

Example: force booting to BIOS for multiple machines:

    $ fce-ipmi bootdev bios compute-[13]
    INFO: compute-1: Set Boot Device to bios
    INFO: compute-3: Set Boot Device to bios

Example: open a SOL console with compute-2.example.com:

    $ fce-ipmi console compute-2

See below for more examples.

## Installation

```
git clone git@github.com:phausman/fce-ipmi.git
cd fce-ipmi
sudo python3 setup.py install
```

# fce-ipmi

`fce-ipmi [OPTIONS] COMMAND [ARGS]...`

`fce-ipmi` is a wrapper for `ipmitool` utility. Therefore you must have 
`ipmitool` installed in your system. On Ubuntu you can install it with
`sudo apt install ipmitool`.

The wrapper pulls necessary information about the machines, such as BMC
hostname / IP address, username and password from the YAML file. By default
`./config/nodes.yaml` file is parsed for this information. You can explicitly
specify the location of machines config file with an option 
`-f, --machine-config`.

Alternatively, the file can be specified in the configuration file
(`~/.local/share/fce-ipmi/config`) as a vaulue of the key
`machine-config-path`. [NOT IMPLEMENTED]

This tool supports bash completion. Press `tab` key twice to display
available commands, parameters, machine names etc. [NOT IMPLEMENTED]

## Options

`-d, --debug`          Enable debug log level.

`-s, --dry-run`        Simulate running the command.

`-f, --machine-config` Path to the YAML file with machines' configuration.

`--no-color`           Disable colored output. [NOT IMPLEMENTED]

`-v, --verbose`        Be more verbose. [NOT IMPLEMENTED]

`-V, --version`        Print program version.

`--help`               Display help.

Global options must be provided right after the program name. 

# Commands

## `power [OPTIONS] {on|off|cycle|stat} [MACHINE-NAME ...]`

Controls the power of one or more machines. You can request 
powering on, off or power cycling the machine(s). `stat` command reads the 
current power state of the machine(s).

If `power` command is run without a specified power action, the `stat` action 
is executed by default.

If `MACHINE-NAME` is not specified, the action is executed against all
machines.

Multiple `MACHINE-NAME`s can be specified.

`MACHINE-NAME` accepts glob patterns. For example, running the command 
`power on compute-*`, will result in powering on all machines whose name begins 
with `compute-`.

You can specify a partial machine name and the tool will try to guess its 
full name. For example, if the machine's full name is `compute-1.dc.example.com`
it is enough to refer to this machine as `compute-1`.

This command is a wrapper for `ipmitool` utility. It executes `ipmitool` with 
relevant parameters, such as `chassis power on`, `chassis power off`, 
`chassis power status` or `chassis power cycle`.

### Command options

#### `-i, --include PATTERN` [NOT IMPLEMENTED]

The machines specified in the `PATTERN` will be included in the list of 
machines selected for executing the command upon them.

Providing the `MACHINE-NAME` is an equivalent to specifying 
`--include name=MACHINE-NAME`.

Multiple properties, separated by comma can be specified, e.g.
`--include name=storage-*,tags=AZ1`. The properties separated by comma are
applied according to logical 'AND' operation.

You can also specify multiple `--include` options. In such a case the
resulting list of machines will be the outcome of a logical 'OR' operation
between all `--include` options.

#### `-x, --exclude PATTERN` [NOT IMPLEMENTED]

This option excludes machines specified in the `PATTERN` from running the 
action upon them.

By default, `PATTERN` applies to the machine name and is equivalent to 
specifying `--exclude name=MACHINE-NAME`. You can specify other machine 
properties, e.g. tags, zone, etc.

Similarly to `--include` option, this option also supports multiple instances
(joined as logical 'OR') and comma-separated properties.

### Examples of `power` command

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

## `bootdev {bios|disk|pxe} [MACHINE-NAME ...]`

Set boot option for the next power cycle.

This command is a wrapper for `ipmitool` utility. It executes `ipmitool` with 
relevant parameters, such as `chassis bootdev bios`, `chassis bootdev disk` or 
`chassis bootdev pxe`.

### Command options

#### `-i, --include PATTERN` [NOT IMPLEMENTED]

The machines specified in the `PATTERN` will be included in the list of machines
selected for executing the command upon them. See more detailed description of 
this option in the `power` command section.

#### `-x, --exclude PATTERN` [NOT IMPLEMENTED]

This option excludes machines specified in the pattern from running the action 
upon them. See more detailed description of this option in the `power` command 
section.

### Examples of `bootdev` command

Set boot to BIOS for all storage nodes:

    fce-ipmi bootdev bios storage-*

Set PXE boot for all nodes:

    fce-ipmi bootdev pxe

Set boot to disk for all machines in availability zones `AZ1` and `AZ2`

    fce-ipmi bootdev disk --include zone=AZ1 --include zone=AZ2

## `console MACHINE-NAME` [NOT IMPLEMENTED]

This command opens a Serial-over-LAN console with a specified machine. You can 
exit the console by typing '&.' sequence.

This command is a wrapper for `ipmitool sol activate`. The wrapper executes
`ipmitool` with relevant options such as a username and password.

### Examples of `console` command

Open the console with `compute-1` machine:

    fce-ipmi console compute-1
