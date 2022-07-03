"""Pytest setup."""
import os
from pathlib import Path
from typing import Dict, List

import pytest
from dotenv import find_dotenv, load_dotenv
from rich import pretty, traceback
from rich.console import Console
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from src.resources.robot_data import ROBOT_MAPPING, RobotDataType

collect_ignore_glob = ["files/**/*.py"]

_console = Console(log_time=True)
pretty.install(console=_console)
traceback.install(console=_console)


# Check to see if we have a dotenv file and use it
if find_dotenv():
    load_dotenv(find_dotenv())


def pytest_collection_modifyitems(items):  # type: ignore # noqa: ANN201,ANN001
    """Order tests."""
    # When running all tests calibrate the robot first.
    # Most other tests require this.
    MODULE_ORDER = ["tests.calibrate_test"]
    module_mapping = {item: item.module.__name__ for item in items}
    sorted_items = items.copy()
    # Iteratively move tests of each module to the end of the test queue
    for module in MODULE_ORDER:
        sorted_items = [it for it in sorted_items if module_mapping[it] == module] + [
            it for it in sorted_items if module_mapping[it] != module
        ]
    items[:] = sorted_items


def _chrome_options() -> Options:
    """Chrome options for setup."""
    options = Options()
    executable_path = os.getenv("EXECUTABLE_PATH")
    assert (
        executable_path is not None
    ), "EXECUTABLE_PATH environment variable must be set"
    _console.print(f"EXECUTABLE_PATH is {executable_path}")
    options.binary_location = executable_path
    options.add_argument("whitelisted-ips=''")  # type: ignore
    options.add_argument("disable-xss-auditor")  # type: ignore
    options.add_argument("disable-web-security")  # type: ignore
    options.add_argument("allow-running-insecure-content")  # type: ignore
    options.add_argument("no-sandbox")  # type: ignore
    options.add_argument("disable-setuid-sandbox")  # type: ignore
    options.add_argument("disable-popup-blocking")  # type: ignore
    options.add_argument("allow-elevated-browser")  # type: ignore
    return options


@pytest.fixture(scope="function")
def driver() -> WebDriver:  # type: ignore
    """Pass standard Chrome options to a test."""
    update_channel = os.getenv("UPDATE_CHANNEL")
    assert update_channel is not None, "UPDATE_CHANNEL environment variable must be set"
    options = _chrome_options()
    os.environ["OT_APP_ANALYTICS__SEEN_OPT_IN"] = "true"
    os.environ["OT_APP_ANALYTICS__OPTED_IN"] = "true"
    os.environ["OT_APP_DISCOVERY__CANDIDATES"] = "localhost"
    os.environ["OT_APP_ANALYTICS__APP_ID"] = "6dcc8733-c3e6-4ac4-b14f-638ede114ac5"
    os.environ["OT_APP_ANALYTICS__USER_ID"] = "b806c211-3b21-4c5e-8b06-aedc58887cce"
    os.environ["OT_APP_UPDATE__CHANNEL"] = update_channel
    os.environ["OT_APP_LOG__LEVEL__CONSOLE"] = "error"
    with webdriver.Chrome(options=options) as driver:  # type: ignore
        _console.print("Driver Capabilities.")
        _console.print(driver.capabilities)
        yield driver


@pytest.fixture(scope="session")
def test_protocols() -> Dict[str, Path]:
    """Provide a fixture with a dictionary of test protocol files."""
    # build this manually for now
    return {
        "python1": Path(
            Path(__file__).resolve().parent,
            "files/protocol/python1/test_drive.py",
        ),
        "protocoluploadjson": Path(
            Path(__file__).resolve().parent,
            "files/protocol/json/upload_protocol.json",
        ),
        "moamjson": Path(
            Path(__file__).resolve().parent,
            "files/protocol/json/moam_pur.json",
        ),
        "gen1pipette": Path(
            Path(__file__).resolve().parent,
            "files/protocol/json/gen1_pipette.json",
        ),
    }


@pytest.fixture(scope="session")
def test_labwares() -> Dict[str, Path]:
    """Provide a fixture with a dictionary of test protocol files."""
    # build this manually for now
    return {
        "validlabware": Path(
            Path(__file__).resolve().parent,
            "files/protocol/json/sample_labware.json",
        ),
        "invalidlabware": Path(
            Path(__file__).resolve().parent,
            "files/protocol/json/invalid_labware.json",
        ),
    }


@pytest.fixture(scope="session")
def console() -> Console:
    """Rich console for output."""
    return _console


@pytest.fixture(scope="session")
def robots() -> List[RobotDataType]:
    """Robot data."""
    # provide all robot data to the tests
    robots = ["dev", "kansas", "emulated_alpha"]
    result = []
    for robot in robots:
        robot_type = ROBOT_MAPPING[robot]
        result.append(robot_type)
    return result
