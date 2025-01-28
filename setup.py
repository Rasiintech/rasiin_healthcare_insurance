from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in rasiin_healthcare_insurance/__init__.py
from rasiin_healthcare_insurance import __version__ as version

setup(
	name="rasiin_healthcare_insurance",
	version=version,
	description="Healthcare Insurance App for Somalia.",
	author="Ahmed Ibar",
	author_email="rasiintech@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
