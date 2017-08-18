'''
## Create python package

- http://peterdowns.com/posts/first-time-with-pypi.html

> MANIFEST.in tells Distutils what files to include in the source distribution
but it does not directly affect what files are installed. For that you need to
include the appropriate files in the setup.py file, generally either as package
data or as additional files. -- stackoverflow, 3596979

https://docs.python.org/3/distutils/setupscript.html#installing-package-data
https://docs.python.org/3/distutils/sourcedist.html#manifest

## Setuptools integration click

http://click.pocoo.org/5/setuptools/#setuptools-integration
'''


from setuptools import setup, find_packages


setup(
    name='nanoql',
    version='0.1',
    description='A DSL to query sequence databases.',
    url='https://github.com/viehwegerlib/nanoql',
    author='Adrian Viehweger',
    author_email='adrian.viehweger@uni-jena.de',
    license='BSD 3-clause',
    packages=find_packages(),
    include_package_data=True,  # use Manifest.in, stackoverflow, 13307408
    install_requires=[
        'Click==6.7',
        'biopython==1.69',
        'requests==2.18.3',
        'graphene==1.4.1'
    ],
    zip_safe=False,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points='''
        [console_scripts]
        nanoql=nanoql.__main__:cli
    ''',
    )
