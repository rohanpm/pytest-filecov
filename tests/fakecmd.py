# A command which does whatever certain env vars tell it to do,
# used from within some tests
from os import environ
import sys
from base64 import b64decode


if __name__ == "__main__":
    infix = sys.argv[1].upper()
    stdout = b64decode(environ.get(f"FAKECMD_{infix}_STDOUT") or "")
    stderr = b64decode(environ.get(f"FAKECMD_{infix}_STDERR") or "")
    exitcode = int(environ.get(f"FAKECMD_{infix}_EXIT") or "0")

    if stdout:
        sys.stdout.buffer.write(stdout)
        sys.stdout.buffer.flush()
    if stderr:
        sys.stderr.buffer.write(stderr)
        sys.stderr.buffer.flush()
    sys.exit(exitcode)
