#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


import os

here = os.path.dirname(os.path.abspath(__file__))
f = open(os.path.join(here,  'README.md'))
long_description = f.read().strip()
f.close()


setup(
    name='django-rest-common',
    version='0.0.6',
    author='Sumit Chachra',
    author_email='chachra@tivix.com',
    url='http://github.com/Tivix/django-rest-common',
    description='Common things every Django REST app needs!',
    packages=find_packages(),
    long_description=long_description,
    keywords='django rest common rest-framework api',
    zip_safe=False,
    install_requires=[
        'Django>=1.5.0',
        'djangorestframework>=2.3.13',
    ],
    test_suite='',
    include_package_data=True,
    # cmdclass={},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
