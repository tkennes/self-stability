#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

setup(
    author="Tom Kennes",
    author_email='tomkennes@skyworkz.nl',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Simulations for assessing self-stability of a system with AWS Auto-Scaler and  Kubernetes Scheduler",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='SSTA',
    name='SSTA',
    packages=find_packages(include=['SSTA', 'SSTA.*']),
    url='https://github.com/tkennes/SSTA',
    version='0.1.0',
    zip_safe=False,
)
