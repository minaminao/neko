from setuptools import setup, find_packages

setup(name="neko",
      version="0.0.1",
      install_requires=["pycryptodome", "z3-solver"],
      package_dir={"": "src"},
      packages=find_packages("src"))
