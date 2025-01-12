from setuptools import setup, Extension

module = Extension('heuristic',
                  sources=['heuristic.cpp'],
                  extra_compile_args=['-std=c++17', '-fPIC'],
                  extra_link_args=['-shared'])

setup(name='Heuristic',
      ext_modules=[module])