import pytest

from .session import FilecovSession


@pytest.hookimpl
def pytest_addoption(parser, pluginmanager):
    group = parser.getgroup("pytest-filecov")
    group.addoption(
        "--filecov",
        default=[],
        action="append",
        help="Gather file coverage metrics for this directory",
    )

    pluginmanager.register(FilecovSession())
