import subprocess


class Ipmitool:
    def __init__(
        self, bmc_user: str, bmc_password: str, bmc_address: str, dry_run=False
    ):

        self.command = [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            bmc_address,
            "-U",
            bmc_user,
            "-P",
            bmc_password,
        ]

        # Do not actually run the command if --dry-run is specified.
        # Instead print the command as it would be executed.
        if dry_run:
            self.command.insert(0, "echo")

    def _execute(self) -> (bool, str):
        """Executes the command

        :return Tuple of command result code and command output.
        """

        try:
            process = subprocess.run(
                self.command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

        except subprocess.SubprocessError as e:
            return False, (
                "Failed to run command: '{}'\n{}".format(
                    " ".join(self.command), e.stdout.decode("utf-8").strip()
                )
            )

        return True, process.stdout.decode("utf-8").strip()

    def _execute_without_checking_output(self) -> (bool, str):
        """Executes the command without capturing its output

        :return Tuple of command result code and command output.
        """

        try:
            # Do not capture stdout
            subprocess.run(self.command, stderr=subprocess.PIPE)

        except subprocess.SubprocessError as e:
            return False, (
                "Failed to run command: '{}'\n{}".format(
                    " ".join(self.command), e.stderr.decode("utf-8").strip()
                )
            )

        # Return the cursor to the beginning of the line
        print("\r", end="")

        return True, None

    def power_stat(self) -> (bool, str):
        self.command.extend(["chassis", "power", "status"])
        return self._execute()

    def power_on(self) -> (bool, str):
        self.command.extend(["chassis", "power", "on"])
        return self._execute()

    def power_off(self) -> (bool, str):
        self.command.extend(["chassis", "power", "off"])
        return self._execute()

    def power_cycle(self) -> (bool, str):
        self.command.extend(["power", "cycle"])
        return self._execute()

    def bootdev_bios(self) -> (bool, str):
        self.command.extend(["chassis", "bootdev", "bios"])
        return self._execute()

    def bootdev_disk(self) -> (bool, str):
        self.command.extend(["chassis", "bootdev", "disk"])
        return self._execute()

    def bootdev_pxe(self) -> (bool, str):
        self.command.extend(["chassis", "bootdev", "pxe"])
        return self._execute()

    def console(self) -> (bool, str):
        self.command.extend(["sol", "activate"])
        return self._execute_without_checking_output()
