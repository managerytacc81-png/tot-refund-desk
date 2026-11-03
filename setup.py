from setuptools import setup, find_packages

setup(
    name="tot-refund-desk",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "tot-refund-desk=totrefund.cli:main",
        ],
    },
)
