from typing import List, Callable, MutableSet, Set, Sequence
import subprocess
import os
from threading import Thread, Event
import csv


from .types import Watcher


def do_inotifywait(
    paths: List[str],
    ready: Event,
    failed: List[Exception],
    on_stop: List[Callable],
    accessed: MutableSet[str],
):
    cmd = ["inotifywait", "-m", "--csv", "-e", "access", "-r"]
    cmd.extend(paths)

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        on_stop.append(proc.kill)

        # We want to wait until the command has established all watches
        # to ensure nothing can be missed.
        # FIXME: this really should be better somehow and not rely on
        # a human-oriented message
        while True:
            line = proc.stderr.readline()
            print("line", line)
            if "Watches established" in line:
                break
            elif not line:
                failed.append(RuntimeError("inotifywait did not initialize correctly"))
                break

        ready.set()

        reader = csv.reader(proc.stdout)
        for row in reader:
            (dir, event, name) = row
            if "ACCESS" not in event:
                continue
            fullpath = os.path.join(dir, name)
            accessed.add(fullpath)

    finally:
        proc.poll()
        if proc.returncode is not None:
            proc.kill()


class InotifyWatcher(Watcher):
    def __init__(self, watched_dirs: Sequence[str]):
        self.watched_dirs = watched_dirs
        self.thread = None
        self.on_stop = []
        self.accessed = set()

    def start(self):
        ready = Event()
        failed = []
        self.thread = Thread(
            name="inotifywait",
            target=do_inotifywait,
            kwargs={
                "paths": self.watched_dirs,
                "ready": ready,
                "failed": failed,
                "on_stop": self.on_stop,
                "accessed": self.accessed,
            },
            daemon=True,
        )
        self.thread.start()

        assert ready.wait(60.0), "inotifywait timed out"

        if failed:
            self.thread.join(60.0)
            raise failed[0]

    def stop(self) -> Set[str]:
        for cb in self.on_stop:
            cb()
        self.thread.join(60.0)
        assert not self.thread.is_alive(), "inotifywait thread did not complete"
        return self.accessed
