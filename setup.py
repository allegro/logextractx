""" setup.py file for project """
try:
    from setuptools import setup  # type: ignore
except ImportError:
    from distutils.core import setup


setup(
    name='logextractx',
    version='0.3.0rc2',
    author='Maho (Lukasz Mach)',
    author_email='lukasz.mach@allegro.pl',
    packages=['logextractx'],
    url='https://github.com/allegro/logextractx',
    license='Apache License v 2.0',
    description='LoggerAdapter, which helps you to propagate context information',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown"
)
