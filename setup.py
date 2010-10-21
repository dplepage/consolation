from setuptools import setup

setup(
    name='consolation',
    version='0.1.1',
    packages=['consolation',],
    license='BSD',
    long_description=open('README.rst').read(),
    install_requires=['plac'],
)
