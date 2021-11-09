# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in oberoi_thermit_report/__init__.py
from oberoi_thermit_report import __version__ as version

setup(
	name="oberoi_thermit_report",
	version=version,
	description="Bhavesh",
	author="Bhavesh Maheshwari",
	author_email="maheshwaribhavesh95863@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
