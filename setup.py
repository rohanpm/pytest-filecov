from setuptools import setup, find_packages


def get_description():
    return "A pytest plugin to detect unused files"


def get_long_description():
    text = open("README.md").read()

    # The README starts with the same text as "description",
    # which makes sense, but on PyPI causes same text to be
    # displayed twice.  So let's strip that.
    return text.replace(get_description() + ".\n\n", "", 1)


setup(
    name="pytest-filecov",
    version="0.1.1",
    author="Rohan McGovern",
    author_email="rohan@mcgovern.id.au",
    url="https://github.com/rohanpm/pytest-filecov",
    license="GNU General Public License",
    description=get_description(),
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=["pytest"],
    entry_points={"pytest11": ["filecov = pytest_filecov.plugin"]},
    classifiers=[
        "Framework :: Pytest",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
)
