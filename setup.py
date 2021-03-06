#!env python3
from setuptools import setup, find_packages, Extension

import os
import sys

boost = os.getenv("CONDA_PREFIX", '')
if not boost:
    print("\n\033[1;31m WARNING: Not in conda environment. Systems extension may not work correctly.\033[0m\n")

# Create d3s directory. If this does not exist, doing "setup.py install develop" will fail to sym-link.
d3s_folder_path = os.path.join(os.path.dirname(__file__), "d3s")
if "develop" in sys.argv and not os.path.exists(d3s_folder_path):
    os.mkdir(d3s_folder_path)
    
link_args = '-Wl,-rpath,' + boost + '/lib'

e = Extension('d3s.systems',
              sources=['cpp/systems.cpp'],
              language='c++',
              extra_compile_args=['-c', '-O3', '-fPIC', '-D_UNIX', '-std=c++11', '-Wno-deprecated-declarations'],
              extra_link_args=[link_args],
              include_dirs=[boost, 'm'],
              libraries=['boost_python37', 'boost_numpy37'],
              )


setup(name='d3s',
      version='0.1',
      ext_modules=[e],
      packages=find_packages(),
      include_package_data=True,
)
