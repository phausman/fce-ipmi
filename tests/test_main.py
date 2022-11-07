from unittest.mock import patch, mock_open

import pytest

import messages
import main


@pytest.mark.parametrize("option", ["-V", "--version"])
def test_version(cli_runner, option):
    result = cli_runner.invoke(main.cli, [option])
    assert result.exit_code == 0
    assert result.output == main.VERSION + "\n"


#
# Test help messages
#


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_cli_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, [option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.MAIN_HELP.split()) in "".join(result.output.split())


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["power", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_LONG_HELP.split()) in "".join(result.output.split())


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_on_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["power", "on", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_ON_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_off_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["power", "off", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_OFF_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_status_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["power", "status", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_STATUS_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["bootdev", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_LONG_HELP.split()) in "".join(result.output.split())


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_bios_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["bootdev", "bios", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_BIOS_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_disk_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["bootdev", "disk", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_DISK_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_pxe_help(cli_runner, option):
    result = cli_runner.invoke(main.cli, ["bootdev", "pxe", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_PXE_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


def test_power_bmc_password_from_file(cli_runner):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: include-rel://bmc-password.txt
  bmc_address: 10.10.10.10
    """

    bmc_password = "password-from-file"

    mo = mo1 = mock_open(read_data=machines_config_yaml)
    mo2 = mock_open(read_data=bmc_password)

    mo.side_effect = [mo1.return_value, mo2.return_value]

    with patch("builtins.open", mo):
        result = cli_runner.invoke(
            main.cli,
            [
                "-s",
                "--no-color",
                "power",
                "status",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert (
            result.output == "INFO: test-machine-1: ipmitool -e & -I lanplus "
            "-H 10.10.10.10 "
            "-U user "
            "-P password-from-file "
            "chassis power status\n"
        )


def test_power_bmc_password_from_file_error(cli_runner):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: include-rel://bmc-password.txt
  bmc_address: 10.10.10.10
    """

    bmc_password = "password-from-file"

    mo = mo1 = mock_open(read_data=machines_config_yaml)
    mo2 = mock_open(read_data=bmc_password)
    mo2.return_value = 1
    mo2.side_effect = FileNotFoundError

    mo.side_effect = [mo1.return_value, FileNotFoundError]

    with patch("builtins.open", mo):
        result = cli_runner.invoke(
            main.cli,
            [
                "-s",
                "--no-color",
                "power",
                "status",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 1
        assert (
            "Cannot open 'bmc-password.txt' file referred in "
            "the 'bmc_password' value" in result.output
        )


def test_power_status_implicit(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            ["power"],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls


def test_power_no_machines(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            ["power", "status"],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls


def test_power_single_machine(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                "status",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls


@pytest.mark.parametrize("command", ["on", "off", "cycle", "status"])
def test_power_commands_single_machine(cli_runner, fake_process, command):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                command,
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            command,
        ] in fake_process.calls, str(fake_process.calls)


@pytest.mark.parametrize("command", ["disk", "pxe"])
def test_bootdev_commands_single_machine(cli_runner, fake_process, command):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "bootdev",
                command,
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "bootdev",
            command,
        ] in fake_process.calls, str(fake_process.calls)


@pytest.mark.parametrize("command", ["bios"])
def test_bootdev_bios_single_machine(cli_runner, fake_process, command):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "bootdev",
                command,
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "bootdev",
            command,
            "options=efiboot",
        ] in fake_process.calls, str(fake_process.calls)


def test_console_single_machine(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "console",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "sol",
            "activate",
        ] in fake_process.calls, str(fake_process.calls)


def test_power_multiple_machines(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
test-machine-2:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.20
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                "status",
                "test-machine-1",
                "test-machine-2",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.20",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls


def test_power_glob_multiple_machines(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
test-machine-2:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.20
test-machine-3:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.30
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                "status",
                "test-machine-[12]",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.20",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls


def test_power_glob_multiple_machines_multiple_arguments(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
test-machine-2:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.20
test-machine-3:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.30
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                "status",
                "test-machine-[1]",
                "test-machine-[2]",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.20",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls


def test_power_single_machine_short_name(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1.example.com:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                "status",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert [
            "ipmitool",
            "-e",
            "&",
            "-I",
            "lanplus",
            "-H",
            "10.10.10.10",
            "-U",
            "user",
            "-P",
            "password",
            "chassis",
            "power",
            "status",
        ] in fake_process.calls


def test_power_single_machine_debug(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1.example.com:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "--debug",
                "power",
                "status",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert "Running command Command.POWER_STATUS with parameters" in result.output


def test_power_single_machine_debug_no_color(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1.example.com:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(["ipmitool", fake_process.any()])

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "--debug",
                "--no-color",
                "power",
                "status",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 0
        assert "Running command Command.POWER_STATUS with parameters" in result.output


def callback_function_file_not_found(process):
    raise FileNotFoundError("exception raised by subprocess")


def callback_function_subprocess_error(process):
    from subprocess import SubprocessError

    raise SubprocessError("exception raised by subprocess")


@pytest.mark.parametrize(
    "callback_function",
    [callback_function_file_not_found, callback_function_subprocess_error],
)
def test_power_failed_subprocess(cli_runner, fake_process, callback_function):
    machines_config_yaml = """test-machine-1.example.com:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(
        ["ipmitool", fake_process.any()], callback=callback_function
    )

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                "status",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 1


@pytest.mark.parametrize(
    "callback_function",
    [callback_function_file_not_found, callback_function_subprocess_error],
)
def test_console_failed_subprocess(cli_runner, fake_process, callback_function):
    machines_config_yaml = """test-machine-1.example.com:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
    """
    fake_process.register_subprocess(
        ["ipmitool", fake_process.any()], callback=callback_function
    )

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "console",
                "test-machine-1",
            ],
        )
        assert result.exit_code == 1


def test_console_glob(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
test-machine-2:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.20
    """

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "console",
                "test-machine-*",
            ],
        )
        assert result.exit_code == 1
        assert (
            "Glob patterns for MACHINE-NAME are not supported for this command"
            in result.output
        )


def test_no_machines_found(cli_runner, fake_process):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
test-machine-2:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.20
    """

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "console",
                "test-machine-3",
            ],
        )
        assert result.exit_code == 1
        assert "No machines matching name 'test-machine-3' found" in result.output


def test_no_machines_found_empty_machines_config(cli_runner):
    machines_config_yaml = ""

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "console",
                "test-machine-3",
            ],
        )
        assert result.exit_code == 1
        assert "Could not read machines from machines config file" in result.output


def test_ambiguous_machine_name(cli_runner):
    machines_config_yaml = """test-machine-1:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.10
test-machine-2:
  bmc_user: user
  bmc_password: password
  bmc_address: 10.10.10.20
    """

    with patch("builtins.open", mock_open(read_data=machines_config_yaml)):
        result = cli_runner.invoke(
            main.cli,
            [
                "power",
                "on",
                "test-machine",
            ],
        )
        assert result.exit_code == 1
        assert "Ambiguous machine name provided" in result.output


def test_power_status_dry_run(cli_runner):
    result = cli_runner.invoke(
        main.cli,
        [
            "-s",
            "--no-color",
            "-f",
            "tests/config/nodes.yaml",
            "power",
            "status",
            "compute-1",
        ],
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "INFO: compute-1.example.com: ipmitool -e & -I lanplus -H 192.168.200.1 "
        "-U root -P p4ssw0rd! chassis power status\n"
    )


# https://medium.com/opsops/how-to-test-if-name-main-1928367290cb
def test_init():
    with patch.object(main, "cli"):
        with patch.object(main, "__name__", "__main__"):
            main.init()
            assert main.cli.called
