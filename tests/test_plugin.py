# High-level test of the entire plugin.
from unittest import mock
import argparse

from pluggy import PluginManager

import pytest_filecov.plugin


class FakePluginManager:
    def __init__(self):
        self.registered = None

    def register(self, plugin):
        assert not self.registered
        self.registered = plugin


class FakeConfig:
    def __init__(self, filecov):
        self.filecov = filecov

    @property
    def option(self):
        return self


def test_plugin_noop():
    parser = mock.Mock(spec=["getgroup", "addoption"])
    pm = FakePluginManager()
    pytest_filecov.plugin.pytest_addoption(parser, pm)

    # Should have registered
    assert pm.registered

    # Do a test in the case where no monitoring is requested
    config = FakeConfig([])

    plugin = pm.registered

    # These should all work and do effectively nothing
    plugin.pytest_configure(config)
    plugin.pytest_sessionstart(object())
    plugin.pytest_sessionfinish(object())
    assert plugin.pytest_report_header(object(), object()) == []
    plugin.pytest_terminal_summary(object())
