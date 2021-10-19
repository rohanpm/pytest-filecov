from typing import Iterable, Sequence

import subprocess


class GitLsFiles:
    def __init__(self, dirs: Sequence[str]):
        self.dirs = dirs

    def __iter__(self) -> Iterable[str]:
        cmd = ["git", "ls-files", "-z"]
        cmd.extend(self.dirs)
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
        names = proc.stdout.split(b"\x00")
        return sorted([name.decode() for name in names if name]).__iter__()
