import os

import pkg_resources
from setuptools import find_packages
from setuptools import setup


def read_version(fname="whisper_api/version.py"):
    exec(compile(open(fname, encoding="utf-8").read(), fname, "exec"))
    return locals()["__version__"]


setup(
    name="karaoke_queue",
    version=read_version(),
    url="https://github.com/nonchris/karaoke_queue",
    license="",
    author="nonchris",
    author_email="info@nonchris.eu",
    description="A queue for karaoke",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    readme="README.md",
    python_requires=">=3.9",
    packages=find_packages(where='src', exclude=["tests*"]),
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    entry_points={
        "console_scripts": ["karaoke_queue=karaoke_queue.webserver:start"],
    },
    include_package_data=True,
)
