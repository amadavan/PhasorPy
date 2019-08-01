from setuptools import setup, find_packages

setup(
    name='phasorpy',
    version='0.1.0',
    packages=['phasorpy'],
    package_dir={'phasorpy': 'phasor'},
    package_data={'phasorpy': ['data/*.m']},
    author='Avinash Madavan',
    author_email='avinash.madavan@gmail.com',
    description='A python library for solving economic dispatch problems for MATPOWER case files.',
    long_description='This library provides operations to load MATPOWER .m files and several functions that are '
                     'frequently used in the MATPOWER library. This allows one to leverage the existing literature '
                     'from MATPOWER without the need for MATLAB.',
    install_requires=[
        'numpy>=1.14.2',
        'scipy>=1.0.0'
    ],
    license='MIT',
)
