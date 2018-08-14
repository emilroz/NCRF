import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import multiprocessing
assert multiprocessing  # silence flake8

version = '0.1.0'


def get_requirements(suffix=''):
    with open('requirements%s.txt' % suffix) as f:
        rv = f.read().splitlines()
    return rv


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def read(fname):
    """
    Utility function to read the README file.
    :rtype : String
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='ncrf-wsi',
      version=version,
      description='',
      long_description='',
      classifiers=[],
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(),
      zip_safe=True,
      include_package_data=True,
      platforms='any',
      setup_requires=['flake8'],
      install_requires=get_requirements(),
      tests_require=get_requirements('-dev'),
      cmdclass={'test': PyTest},
      entry_points={
                'console_scripts': [
                    'camelyon16xml2json = wsi.bin.camelyon16xml2json:main',
                    'json2omero = wsi.bin.json2omeromain'
                ]},
      )
