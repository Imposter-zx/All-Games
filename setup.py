from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='retro-terminal-arcade',
    version='1.0.0',
    description='A collection of retro arcade games playable in the terminal.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Imposter-zx',
    url='https://github.com/Imposter-zx/All-Games',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-chess==0.31.4',
        'colorama'
    ],
    entry_points={
        'console_scripts': [
            'retro-arcade=terminal_games.arcade:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires='>=3.6',
)
