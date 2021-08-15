try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
try:
    import builtins
except ImportError:
    # Python 2 compat: just to be able to declare that Python >=3.5 is needed.
    import __builtin__ as builtins

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Topic :: Software Development',
    'Topic :: Scientific/Engineering',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
]


setup(name='s3s',
    version='1.0.0',
    description='Simplified interface to Amazon AWS S3 data storage service.',
    long_description=open('README.md').read(),
    url='https://github.com/iaroslav-ai/s3s',
    license='MIT',
    author='The S3S contributors',
    classifiers=CLASSIFIERS,
    packages=['s3s'],
    install_requires=open('requirements.txt').read().split('\n'),
)
