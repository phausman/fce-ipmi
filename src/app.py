"""This module contains main Application class.

The class implements core logic of the program.
"""

import fnmatch
import logging
import logging.handlers
from enum import Enum

import colorlog

import utils

import yaml

CLI_OK = 0
CLI_ERROR = 1


class Command(Enum):
    """The enum of command types."""

    POWER_STAT = 1
    POWER_ON = 2
    POWER_OFF = 3
    POWER_CYCLE = 4
    BOOTDEV_BIOS = 5
    BOOTDEV_DISK = 6
    BOOTDEV_PXE = 7
    CONSOLE = 8


class Application:
    """Main application class."""

    DEFAULT_MACHINE_CONFIG_PATH = "./config/nodes.yaml"

    def __init__(
        self,
        debug=False,
        dry_run=False,
        machine_config="",
        no_color=False,
        verbose=False,
    ):
        """Set up logger and read node config file."""
        # Read global options
        self.debug = debug
        self.dry_run = dry_run
        self.machine_config = (
            machine_config if machine_config else self.DEFAULT_MACHINE_CONFIG_PATH
        )
        self.no_color = no_color
        self.verbose = verbose

        # Configure logger
        self.logger = self._get_logger() if no_color else self._get_colored_logger()

    def _get_logger(self):
        """Create and return a logger object."""
        # Create a logger
        logger = logging.getLogger(__name__)

        if self.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # Create console formatter
        console_format = "%(levelname)s: %(message)s"
        console_formatter = logging.Formatter(fmt=console_format)

        # Create a console handler: log to console
        console_handler = logging.StreamHandler()

        # Configure and register console handler
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def _get_colored_logger(self):
        """Create and return a colored logger object."""
        # Create a logger
        logger = colorlog.getLogger(__name__)

        if self.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # Create console formatter
        console_format = "%(log_color)s%(message)s"
        console_formatter = colorlog.ColoredFormatter(fmt=console_format)

        # Create a console handler: log to console
        console_handler = colorlog.StreamHandler()

        # Configure and register console handler
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def _read_machines_config(self) -> dict:
        """Read YAML machine config file.

        :return Dictionary with machines' details or None if details
                could not be retrieved.
        """
        # Python representation of the YAML machine config file
        machines = None

        try:
            with open(self.machine_config) as file:
                machines = yaml.load(file, Loader=yaml.FullLoader)
                self.logger.debug(
                    f"Read machines from {self.machine_config}: {machines}"
                )

        except yaml.YAMLError as e:
            self.logger.error(f"Error in machines configuration file: {e}")

        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            self.logger.error(
                f"Cannot open machines configuration file: '{self.machine_config}'"
            )
            self.logger.error(e)

        return machines

    def _is_glob_pattern(self, text: str) -> bool:
        """Check if the string is a glob pattern."""
        # Characters used in glob patterns. A string containig these
        # characters is a glob pattern.
        glob_pattern_characters = set("*?[")

        if not any((char in glob_pattern_characters) for char in text):
            return False

        return True

    def _get_matching_machines(self, machines, include, exclude) -> list:
        """Find matching machines.

        Evaluate command parameters against the machines
        found in the config file and return the list or matching
        machines.

        :param machines: Tuple of machine names. Multiple machine names can
        be provided.
        """
        # A set for storing matching machine names. Casted to a list,
        # this is used as a return value of this function.
        matching_machines = set()

        # Create a list of machines so that it can be modifed
        machines = list(machines)

        # If no machine name was provided, assume all machines should match
        if len(machines) == 0:
            self.logger.debug(
                "No machine name(s) provided, assuming all machines match"
            )
            machines.append("*")

        # Build a list of machine names pulled from the config file
        config_machine_names = []
        for k, v in self.machines.items():
            config_machine_names.append(k)

        # Return early if no machines were found in the config file
        if len(config_machine_names) == 0:
            self.logger.warning(f"No machines found in {self.machine_config}")
            return []

        # Iteratively build a set of maching machine names
        for machine in machines:

            # Treat a machine name as a glob pattern
            pattern = machine

            if self._is_glob_pattern(machine) is False:
                # Machine name is not a glob pattern. Explicitly make it
                # a glob pattern so that "guessing" a full machine name from
                # the partial string can be implemented.
                pattern = "*{}*".format(pattern)

            # Find matching machine names
            matches = fnmatch.filter(config_machine_names, pattern)

            for match in matches:
                matching_machines.add(match)

            # Multiple machines found, but at least one of the machine names
            # provided was not a glob pattern. Cancel a command (by returning
            # an empty list) and inform the user that more than one machine
            # matching the pattern was found.
            if (len(matches) > 1) and (self._is_glob_pattern(machine) is False):
                message = (
                    "Ambiguous machine name provided. "
                    "Found {} machines matching '{}' name:\n  {}\n"
                    "Refine the '{}' machine name pattern by adding more "
                    "details to target a specific machine.\n"
                    "Alternatively, for commands that support multiple "
                    "MACHINE-NAMEs (such as power or bootdev), you can "
                    "provide a glob pattern to target more than one "
                    "machine, e.g. '*{}*'.".format(
                        len(matches),
                        machine,
                        "\n  ".join(matches),
                        machine,
                        machine,
                    )
                )

                self.logger.warning(message)
                return []

        # None of the machine names matches, return an empty list
        if len(matching_machines) == 0:
            message = (
                "No machines matching name '{}' found. "
                "Available machines:\n  {}".format(
                    "' or '".join(machines), "\n  ".join(self.machines)
                )
            )
            self.logger.warning(message)
            return []

        # Return a sorted list of matching machines
        matching_machines = list(matching_machines)
        matching_machines.sort()

        return matching_machines

    def _execute_wrapper(self, command: Command, machine: str) -> (bool, str):

        utility = utils.Ipmitool(
            self._get_config_value(self.machines[machine], "bmc_user"),
            self._get_config_value(self.machines[machine], "bmc_password"),
            self._get_config_value(self.machines[machine], "bmc_address"),
            self.dry_run,
        )

        # Execute the command

        if command == Command.POWER_STAT:
            return utility.power_stat()

        if command == Command.POWER_ON:
            return utility.power_on()

        if command == Command.POWER_OFF:
            return utility.power_off()

        if command == Command.POWER_CYCLE:
            return utility.power_cycle()

        if command == Command.BOOTDEV_BIOS:
            return utility.bootdev_bios()

        if command == Command.BOOTDEV_DISK:
            return utility.bootdev_disk()

        if command == Command.BOOTDEV_PXE:
            return utility.bootdev_pxe()

        if command == Command.CONSOLE:
            return utility.console()

    def _run_command(self, command: Command, machines: list):
        """Run command on all machines.

        :return: CLI_OK if all commands were successful, CLI_ERROR otherwise
        """
        self.logger.debug(f"Running command {command} on machines: {machines}")

        return_code = CLI_OK

        # For each machine in the list
        for machine in machines:

            # Execute the command...
            success, output = self._execute_wrapper(command, machine)

            # And print the result
            if success:
                if output:
                    self.logger.info("{}: {}".format(machine, output))
            else:
                return_code = CLI_ERROR
                output = output if output else "Command failed without any output"
                self.logger.error("{}: {}".format(machine, output))

        return return_code

    def _get_config_value(self, machine: dict, key: str) -> str:

        # Default return value
        value = machine[key]

        # If the value starts with this pattern, read the value from the file
        include_rel_pattern = "include-rel://"

        if machine[key].startswith(include_rel_pattern):

            # Get the file path by removing the include-file:// pattern
            file_path = machine[key].replace(include_rel_pattern, "")

            try:
                with open(file_path) as file:
                    value = file.read().strip()

            except (FileNotFoundError, PermissionError) as e:
                self.logger.error(
                    f"Cannot open '{file_path}' file referred in the '{key}' value"
                )
                self.logger.error(e)
                exit(1)

        return value

    def run(self, command: Command, machines, include, exclude):
        """Build a list of applicable machines and execute an action upon them.

        :return: CLI_OK if successful, CLI_ERROR on error.
        """
        self.logger.debug(
            "Running command {} with parameters: "
            "machines={}, include={}, exclude={}".format(
                command, machines, include, exclude
            )
        )

        # Read YAML file containing BMC details of machines
        machines_from_config = self._read_machines_config()
        if machines_from_config:
            self.machines = machines_from_config
        else:
            # Could not read machines from config file
            return CLI_ERROR

        # Exit early if glob pattern is provided for the command that
        # does not support it
        if (command is Command.CONSOLE) and self._is_glob_pattern(machines[0]):
            self.logger.warning(
                "Glob patterns for MACHINE-NAME are not supported in this command"
            )
            return CLI_ERROR

        # Build a list of machines matching the request
        matching_machines = self._get_matching_machines(machines, include, exclude)

        # Execute an action on the machines
        return self._run_command(command, matching_machines)
