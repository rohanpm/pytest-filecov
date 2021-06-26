from typing import List, Callable, MutableSet, Set, Sequence
import subprocess
import os
from threading import Thread, Event
import csv


from .types import Watcher


def do_inotifywait(
    paths: List[str], ready: Event, on_stop: List[Callable], accessed: MutableSet[str]
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
            if "Watches established" in line:
                break
            elif not line:
                raise RuntimeError("inotifywait failed")

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
        self.thread = Thread(
            name="inotifywait",
            target=do_inotifywait,
            kwargs={
                "paths": self.watched_dirs,
                "ready": ready,
                "on_stop": self.on_stop,
                "accessed": self.accessed,
            },
            daemon=True,
        )
        self.thread.start()

        # TODO: complain if not ready
        ready.wait(60.0)

    def stop(self) -> Set[str]:
        for cb in self.on_stop:
            cb()
        self.thread.join(5.0)
        if self.thread.is_alive():
            # TODO
            print("thread didn't complete")
        return self.accessed
