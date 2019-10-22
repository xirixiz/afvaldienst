from setuptools import setup
from codecs import open
import os
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def readme():
    with open('README.rst', 'r', 'utf-8') as f:
        readme = f.read()
    with open('HISTORY.rst', 'r', 'utf-8') as f:
        history = f.read()
    return readme + '\n\n' + history


setup(name='afvaldienst',
      version=find_version("Afvaldienst", "__init__.py"),
      description='Getting information on trash for the Netherlands for mijnafvalwijzer.nl and afvalstoffendienstkalender.nl',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://github.com/xirixiz/afvaldienst',
      author='Bram van Dartel',
      author_email='spam@rootrulez.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Other Audience',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Natural Language :: English',
          'Natural Language :: Dutch',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Unix',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='afval afvaldienst afvalwijzer garbage trash mijnafvalwijzer afvalstoffendienstkalender dutch',
      packages=['Afvaldienst'],
      install_requires=['requests'],
      include_package_data=True,
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      zip_safe=False)
