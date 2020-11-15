import pytest

from click.testing import CliRunner

import messages
import main


@pytest.mark.parametrize("option", ["-V", "--version"])
def test_version(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, [option])
    assert result.exit_code == 0
    assert result.output == main.VERSION + "\n"


#
# Test help messages
#


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_cli_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, [option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.MAIN_HELP.split()) in "".join(result.output.split())


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["power", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_LONG_HELP.split()) in "".join(result.output.split())


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_on_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["power", "on", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_ON_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_off_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["power", "off", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_OFF_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_power_stat_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["power", "stat", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.POWER_STAT_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["bootdev", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_LONG_HELP.split()) in "".join(result.output.split())


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_bios_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["bootdev", "bios", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_BIOS_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_disk_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["bootdev", "disk", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_DISK_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_bootdev_pxe_help(option):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["bootdev", "pxe", option])
    assert result.exit_code == 0
    # Strip all whitespace before comparing strings because click rewraps test
    assert "".join(messages.BOOTDEV_PXE_ACTION_LONG_HELP.split()) in "".join(
        result.output.split()
    )


#
# commands tests
#

# SUCCESSFUL
# - single machine with short name
# - explicit (without globs) multiple machines
# - glob machine
# - multiple glob machines

# ERRORS
# - glob for console command
# - ambiguous machine name


def test_main(script_runner):
    ret = script_runner.run("fce-ipmi", "--version")
    assert ret.success
    assert ret.stdout == main.VERSION + "\n"
    assert ret.stderr == ""


def test_power_stat_implicit_failed():
    runner = CliRunner()
    result = runner.invoke(main.cli, ["power"])
    assert result.exit_code == 1


@pytest.mark.parametrize("actions", ["on", "off", "cycle", "stat"])
@pytest.mark.parametrize("machines", ["compute-1"])
def test_power_actions_failed(actions, machines):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["power", actions, machines])
    assert result.exit_code == 1


@pytest.mark.parametrize("actions", ["bios", "disk", "pxe"])
@pytest.mark.parametrize("machines", ["compute-1"])
def test_bootdev_actions_failed(actions, machines):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["bootdev", actions, machines])
    assert result.exit_code == 1


@pytest.mark.parametrize("machines", ["compute-1"])
def test_console_failed(machines):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["console", machines])
    assert result.exit_code == 1


def test_power_stat_dry_run():

    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "-s",
            "--no-color",
            "-f",
            "tests/config/nodes.yaml",
            "power",
            "stat",
            "compute-1",
        ],
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "INFO: compute-1.example.com: ipmitool -e & -I lanplus -H 192.168.200.1 "
        "-U root -P p4ssw0rd! chassis power status\n"
    )
