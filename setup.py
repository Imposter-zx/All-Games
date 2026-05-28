from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='retro-terminal-arcade',
    version='2.0.0',
    description='A collection of retro arcade games playable in the terminal.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Imposter-zx',
    url='https://github.com/Imposter-zx/All-Games',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-chess>=0.31.4',
        'colorama>=0.4.0',
        'dataclasses; python_version < "3.7"',
    ],
    entry_points={
        'console_scripts': [
            'retro-arcade=terminal_games.arcade:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Games/Entertainment :: Arcade",
    ],
    python_requires='>=3.6',
)
