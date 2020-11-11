import fnmatch
import logging
import logging.handlers
import yaml
from enum import Enum

import utils


class Application:
    """Main application class"""

    class Command(Enum):
        POWER_STAT = 1
        POWER_ON = 2
        POWER_OFF = 3
        POWER_CYCLE = 4
        BOOTDEV_BIOS = 5
        BOOTDEV_DISK = 6
        BOOTDEV_PXE = 7

    def __init__(
        self,
        debug=False,
        dry_run=False,
        machine_config="",
        no_color=False,
        verbose=False,
    ):
        # Read global options
        self.debug = debug
        self.dry_run = dry_run
        self.machine_config = machine_config
        self.no_color = no_color
        self.verbose = verbose

        # Configure logger
        self.logger = self._get_logger()

        # Read YAML file containing BMC details of machines
        self.machines = self._read_machines_config()

    def _get_logger(self):
        """Create and return a logger object.

        The logger can be used in this class as follows:

        self.logger.critical("This is critical")
        self.logger.error("This is error")
        self.logger.warning("This is warning")
        self.logger.info("This is info")
        self.logger.debug("This is debug")
        """

        # Create a logger
        logger = logging.getLogger(__name__)

        if self.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # Create console formatter
        CONSOLE_FORMAT = "%(levelname)s: %(message)s"
        console_formatter = logging.Formatter(fmt=CONSOLE_FORMAT)

        # Create a console handler: log to console
        console_handler = logging.StreamHandler()

        # Configure and register console handler
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def _read_machines_config(self) -> dict:
        """Read YAML machine config file

        :return A dictionary with machines' details.
        """

        # Python representation of the YAML machine config file
        machines = {}

        try:
            with open(self.machine_config) as file:
                machines = yaml.load(file, Loader=yaml.FullLoader)

        except (FileNotFoundError, PermissionError, NotADirectoryError) as e:
            self.logger.error(
                f"Cannot open '{self.machine_config}' file "
                f"with machines' BMC config"
            )
            self.logger.error(e)
            exit(1)

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
        """Evaluate command parameters against the machines
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
            machines.append("*")

        # Build a list of machines' names pulled from the config file
        config_machine_names = []
        for k, v in self.machines.items():
            config_machine_names.append(k)

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
            if (len(matches) > 1) and (
                self._is_glob_pattern(machine) is False
            ):
                message = (
                    "Ambiguous machine name provided\n"
                    "Found {} machines matching '{}' name:\n  {}\n"
                    "Refine the '{}' machine name pattern by adding more "
                    "details if you want to target a specific machine.\n"
                    "Alternatively, if you want to target more machines, "
                    "provide a glob machine name pattern, e.g. '*{}*'.".format(
                        len(matches),
                        machine,
                        "\n  ".join(matches),
                        machine,
                        machine,
                    )
                )

                self.logger.error(message)
                return []

        # None of the machine names matches, return an empty list
        if len(matching_machines) == 0:
            message = (
                "No machines matching name '{}' found\n"
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

    def _run_command(self, command: Command, machines: list):

        self.logger.debug(
            "Running command {} on machines: {}".format(command, machines)
        )

        for machine in machines:

            utility = utils.Ipmitool(
                self._get_config_value(self.machines[machine], "bmc_user"),
                self._get_config_value(self.machines[machine], "bmc_password"),
                self._get_config_value(self.machines[machine], "bmc_address"),
                self.dry_run,
            )

            # Execute the command

            if command == self.Command.POWER_STAT:
                success, output = utility.power_stat()

            if command == self.Command.POWER_ON:
                success, output = utility.power_on()

            if command == self.Command.POWER_OFF:
                success, output = utility.power_off()

            if command == self.Command.POWER_CYCLE:
                success, output = utility.power_cycle()

            if command == self.Command.BOOTDEV_BIOS:
                success, output = utility.bootdev_bios()

            if command == self.Command.BOOTDEV_DISK:
                success, output = utility.bootdev_disk()

            if command == self.Command.BOOTDEV_PXE:
                success, output = utility.bootdev_pxe()

            # Print status
            if success:
                self.logger.info("{}: {}".format(machine, output))
            else:
                self.logger.error(
                    "Failed to run command\n" "{}".format(output)
                )

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
                    f"Cannot open '{file_path}' file referred in "
                    f"the '{key}' value"
                )
                self.logger.error(e)
                exit(1)

        return value

    def run(self, command: Command, machines, include, exclude):
        self.logger.debug(
            "Running command {} with parameters: "
            "machines={}, include={}, exclude={}".format(
                command, machines, include, exclude
            )
        )

        # Build a list of machines matching the request
        matching_machines = self._get_matching_machines(
            machines, include, exclude
        )

        # Execute an action on the machines
        self._run_command(command, matching_machines)
