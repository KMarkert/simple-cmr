import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='simplecmr',
      version='0.0.1',
      description='Simple CMR',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/kmarkert/simple-cmr',
      packages=setuptools.find_packages(),
      author='Kel Markert',
      author_email='kel.markert@gmail.com',
      license='MIT',
      zip_safe=False,
      include_package_data=False,
      install_requires=[
          'requests',
          'requests-cache'
      ],
      #entry_points={
      #  'console_scripts': [
      #      'simplecmr = simplecmr.cli:main',
      #  ],
      #},
)
