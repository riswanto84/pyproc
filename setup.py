import re
from setuptools import setup

with open('README.md') as inf:
  long_description = inf.read()

def get_version():
  with open('pyproc/__init__.py') as inf:
      match = re.search(r"((\d\.){2,5}\d)", inf.read(), re.MULTILINE)

      if match is None:
          raise RuntimeError('Version could not be found.')

      return match.groups()[0]

setup(name='pyproc',
      author='mental',
      url='https://github.com/mental32/pyproc.py',
      version=get_version(),
      packages=['pyproc'],
      license='MIT',
      description='A Python preprocessor implementation',
      long_description=long_description,
      include_package_data=True,
)
