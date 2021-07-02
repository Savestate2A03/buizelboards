import setuptools

setuptools.setup(
    name="deerbot-dev",
    version="0.0.1a",
    author="Savestate",
    author_email="joseph.elkhouri@gmail.com",
    description="Personal Discord development bot for friends' servers",
    url="https://github.com/Savestate2A03/deerbot-dev",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)