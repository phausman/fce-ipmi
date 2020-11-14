from main import cli, power_stat
from click.testing import CliRunner


def test_power_stat():

    runner = CliRunner()
    result = runner.invoke(power_stat, ["compute-1"])
    assert result.exit_code == 1


def test_power_stat_dry_run():

    runner = CliRunner()
    result = runner.invoke(
        cli,
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
