from setuptools import setup, find_packages

setup(
    name="PDB-Gizmos",
    author="Abrol Lab",
    version="0.0.1",
    packages=find_packages(),
    scripts=["scripts/SeedFinder.py"],
    install_requires=["mdtraj", "numpy", "scipy", "pandas", "pytraj", "requests", "tabulate"]
)
