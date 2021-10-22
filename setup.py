from setuptools import setup, find_packages

setup(
    name="neko",
    version="0.0.1",
    install_requires=["pycryptodome"],
    package_dir={"":"src"},
    packages=find_packages("src")
)