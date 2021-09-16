import pytest

from app import Application


def test_read_machines_config_file_exists():
    application = Application(machine_config="tests/config/nodes.yaml")
    # Assert that returned dict is not empty
    assert bool(application._read_machines_config()) is True


def test_read_machines_config_file_with_list_exists():
    application = Application(machine_config="tests/config/nodes-list.yaml")
    # Assert that returned dict is not empty
    assert bool(application._read_machines_config()) is True


@pytest.mark.parametrize(
    "machine_config",
    [
        "tests/config/i-dont-exist.yaml",
        "tests/wrong-directory/nodes.yaml",
        "/root/nodes.yaml",
    ],
)
def test_read_machines_config_file_not_found(machine_config):
    application = Application(machine_config=machine_config)
    # Assert that returned dict is empty
    assert bool(application._read_machines_config()) is False


def test_read_machines_config_invalid_yaml():
    application = Application(machine_config="tests/config/nodes-invalid.yaml")
    # Assert that returned dict is empty
    assert bool(application._read_machines_config()) is False


@pytest.mark.parametrize("text", ["compute*", "compute-[12]", "node-?", "node-[!12]"])
def test_is_glob_pattern_returns_true(text):
    application = Application(machine_config="tests/config/nodes.yaml")
    assert application._is_glob_pattern(text) is True


@pytest.mark.parametrize("text", ["compute", ""])
def test_is_glob_pattern_returns_false(text):
    application = Application(machine_config="tests/config/nodes.yaml")
    assert application._is_glob_pattern(text) is False
