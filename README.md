# pytest-filecov

A pytest plugin to detect unused files.

## Overview

This is a pytest plugin to monitor file accesses while tests are running,
then output a report listing files along with whether or not they were
accessed:

```
$ py.test --filecov tests
============================= test session starts ==============================
platform linux -- Python 3.9.5, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
filecov: tests
rootdir: /home/rohan/src/pytest-filecov
plugins: cov-2.12.1, filecov-0.1.0
collected 3 items

tests/test_plugin.py ...                                                 [100%]

============================ pytest-filecov report =============================
Filename                 Covered?
--------                 --------
tests/__init__.py        0
tests/fakecmd.py         1
tests/test_plugin.py     1
tests/some-file          1
tests/other-file         0
============================== 3 passed in 0.13s ===============================
```

## Usage

Prerequisites:

- Linux
- `inotifywait` (try installing `inotify-tools` package)

Install the plugin:

```
pip install pytest-filecov
```

When running your test suite, add `--filecov <path>` specifying the directory
tree(s) for which you'd like a report:

```
py.test --filecov somedir
```

## Why?

This plugin targets the following scenario:

- You've got a large, complex test suite.
- You've got some tests relying on external data stored in files.
- After some refactors, you expect some of the test data files are now unused
  and you'd like to clean them up, but you have no reliable way to determine
  what is or is not used.

Just as `pytest-cov` can help you seek and destroy dead Python code after
refactors, `pytest-filecov` can do the same for dead/unused data files.

## Caveats and missing features

This plugin is rudimentary, with many missing features.

- The format of the reporter is not configurable.
- The list of files included in the report comes from `git ls-files` and
  this is not configurable.
- `.py` files may commonly be listed as uncovered for various reasons
  (e.g. `.pyc` files were used; or files were imported before
  monitoring began)

Contributions to improve any of the above are welcome.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
