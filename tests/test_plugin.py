# High-level test of the entire plugin.
from unittest import mock
import argparse
import textwrap
import os
import sys
from functools import partial
from base64 import b64encode
import io

import py
from pluggy import PluginManager
import pytest

import pytest_filecov.plugin

FAKECMD_PATH = os.path.join(os.path.dirname(__file__), "fakecmd.py")


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


class FakeReporter:
    def __init__(self):
        self.buffer = io.StringIO()

    def write_sep(self, sep, text):
        self.buffer.write(f"{sep * 5} {text} {sep * 5}\n")

    def write_line(self, text):
        self.buffer.write(text + "\n")


def make_fakecmd_base(cmd, *, bindir, exitcode=0, stdout=b"", stderr=b""):
    script = bindir.join(cmd)
    script.write(f"#!/bin/sh\nexec {sys.executable} {FAKECMD_PATH} {cmd}\n")
    script.chmod(0o755)

    cmd = cmd.upper()

    os.environ[f"FAKECMD_{cmd}_EXIT"] = str(exitcode)
    os.environ[f"FAKECMD_{cmd}_STDOUT"] = b64encode(stdout).decode()
    os.environ[f"FAKECMD_{cmd}_STDERR"] = b64encode(stderr).decode()


@pytest.fixture
def make_fakecmd(tmpdir: py.path.local, monkeypatch):
    bindir = tmpdir.mkdir("bin")
    monkeypatch.setenv("PATH", str(bindir) + ":" + os.environ["PATH"])

    yield partial(make_fakecmd_base, bindir=bindir)


def get_plugin():
    parser = mock.Mock(spec=["getgroup", "addoption"])
    pm = FakePluginManager()
    pytest_filecov.plugin.pytest_addoption(parser, pm)

    # Should have registered
    assert pm.registered

    return pm.registered


def test_plugin_noop():
    # Do a test in the case where no monitoring is requested
    config = FakeConfig([])

    plugin = get_plugin()

    # These should all work and do effectively nothing
    plugin.pytest_configure(config)
    plugin.pytest_sessionstart(object())
    plugin.pytest_sessionfinish(object())
    assert plugin.pytest_report_header(object(), object()) == []
    plugin.pytest_terminal_summary(object())


def test_plugin_bad_inotifywait(make_fakecmd):
    make_fakecmd("inotifywait", exitcode=23)

    config = FakeConfig(["dir1", "dir2"])

    plugin = get_plugin()

    plugin.pytest_configure(config)

    # This won't work since inotifywait is broken
    with pytest.raises(Exception) as exc_info:
        plugin.pytest_sessionstart(object())

    assert "inotifywait did not initialize" in str(exc_info)


def test_plugin_typical(make_fakecmd):
    make_fakecmd(
        "inotifywait",
        stderr=b"Watches established\n",
        stdout=b"\n".join(
            [
                b"some/dir,ACCESS,file1",
                b"some/dir,ACCESS,file2",
                b"some/dir,WHATEVER,file2",
                b"some/dir,ACCESS,file3",
            ]
        )
        + b"\n",
    )

    make_fakecmd(
        "git",
        stdout=b"\x00".join([b"some/dir/file1", b"some/dir/file3", b"some/dir/file4"])
        + b"\x00",
    )

    config = FakeConfig(["some", "other"])

    plugin = get_plugin()

    plugin.pytest_configure(config)

    # Should start OK
    plugin.pytest_sessionstart(object())

    # Should finish OK
    plugin.pytest_sessionfinish(object())

    # Should tell me what was monitored
    assert plugin.pytest_report_header(object(), object()) == [
        "filecov: some",
        "filecov: other",
    ]

    # Should output a report
    reporter = FakeReporter()
    plugin.pytest_terminal_summary(reporter)

    assert (
        reporter.buffer.getvalue().strip()
        == textwrap.dedent(
            """
            ===== pytest-filecov report =====
            Filename           Covered?
            --------           --------
            some/dir/file1     1
            some/dir/file3     1
            some/dir/file4     0
            """
        ).strip()
    )
