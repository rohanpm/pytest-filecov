from typing import Optional

from .types import Watcher

from .inotifywatcher import InotifyWatcher
from .gitlist import GitLsFiles


class FilecovSession:
    def __init__(self):
        self.watched_dirs = []
        self.watcher: Optional[Watcher] = None
        self.accessed = set()

    def pytest_configure(self, config):
        self.watched_dirs = config.option.filecov

    def pytest_sessionstart(self, session):
        if not self.watched_dirs:
            return

        self.watcher = InotifyWatcher(self.watched_dirs)
        self.watcher.start()

    def pytest_sessionfinish(self, session):
        self.accessed = self.watcher.stop()

    def pytest_report_header(self, config, startdir):
        return ["filecov: " + path for path in self.watched_dirs]

    def pytest_terminal_summary(self, terminalreporter):
        if not self.watcher:
            return

        file_list = list(GitLsFiles(self.watched_dirs))
        maxlen = max([len(filename) for filename in file_list])
        maxlen = max([maxlen, len("Filename")])

        terminalreporter.write_sep("=", "pytest-filecov report")

        terminalreporter.write_line(f'{"Filename": <{maxlen + 4}} Covered?')
        terminalreporter.write_line(f'{"--------": <{maxlen + 4}} --------')

        for filename in file_list:
            covered = "1" if filename in self.accessed else "0"
            terminalreporter.write_line(f"{filename: <{maxlen + 4}} {covered}")
